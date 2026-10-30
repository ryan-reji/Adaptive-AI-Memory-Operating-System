// ui/electron/main.cjs
"use strict";

const { app, BrowserWindow, dialog } = require("electron");
const path = require("path");
const { execSync } = require("child_process");

const isDev = !app.isPackaged;

const backendManager = isDev ? null : require("./backend-manager.cjs");
const startupCheck = isDev ? null : require("./startup-check.cjs");

// ---------------------------------------------------------------------------
// Python discovery (production only)
// ---------------------------------------------------------------------------

/**
 * Locate a usable Python executable.
 * Search order:
 *   1. <resourcesPath>/python/python.exe  — future embedded Python (Windows)
 *   2. <resourcesPath>/python/python3     — future embedded Python (macOS/Linux)
 *   3. `python` on PATH
 *   4. `python3` on PATH
 * Shows an error dialog and returns null if nothing is found.
 * @returns {string|null}
 */
function findPython() {
  // 1 & 2: Bundled Python (not shipped yet; wired up for future use).
  const bundledCandidates =
    process.platform === "win32"
      ? [path.join(process.resourcesPath, "python", "python.exe")]
      : [path.join(process.resourcesPath, "python", "python3")];

  for (const candidate of bundledCandidates) {
    try {
      require("fs").accessSync(candidate);
      return candidate;
    } catch (_) {
      // Not present — fall through.
    }
  }

  // 3 & 4: System Python on PATH.
  const pathCandidates =
    process.platform === "win32" ? ["python"] : ["python3", "python"];

  for (const candidate of pathCandidates) {
    try {
      const out = execSync(`${candidate} --version`, {
        stdio: ["ignore", "pipe", "ignore"],
        timeout: 3000,
      })
        .toString()
        .trim();
      if (out.toLowerCase().startsWith("python")) {
        return candidate;
      }
    } catch (_) {
      // Not found or timed out — try next.
    }
  }

  // Nothing found.
  dialog.showErrorBox(
    "Recall — Python not found",
    "Python 3.10+ is required to run Recall but was not found on your system.\n\n" +
      "Please install Python from https://python.org, ensure it is added to your PATH, " +
      "then restart Recall."
  );
  return null;
}

// ---------------------------------------------------------------------------
// Window creation
// ---------------------------------------------------------------------------

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 780,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#0f1614",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: "hiddenInset",
  });

  if (isDev) {
    win.loadURL("http://localhost:5173");
    win.webContents.openDevTools({ mode: "detach" });
  } else {
    win.loadFile(path.join(__dirname, "../dist/index.html"));
  }

  return win;
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.whenReady().then(async () => {
  if (!isDev) {
    // --- Find Python ---
    const pythonExecutable = findPython();
    if (!pythonExecutable) {
      app.quit();
      return;
    }

    // Python source is copied here by electron-builder's extraResources rule.
    const workDir = path.join(process.resourcesPath, "app-source");

    // Databases must live in a writable location (resourcesPath is read-only
    // in a signed/installed app). On first run the Python code creates them.
    const userDataDir = app.getPath("userData");
    const memoryDbPath = path.join(userDataDir, "memory.db");
    const sfDbPath = path.join(userDataDir, "recommendations.db");

    // Smart-forgetting needs sklearn 1.5.2 — use the bundled venv if present,
    // otherwise fall back to system Python (which may fail on version mismatch).
    const sfVenvPython = path.join(
      process.resourcesPath,
      "sf-venv",
      "Scripts",
      "python.exe"
    );
    let sfPythonExecutable;
    try {
      require("fs").accessSync(sfVenvPython);
      sfPythonExecutable = sfVenvPython;
    } catch (_) {
      sfPythonExecutable = pythonExecutable; // fallback
    }

    // Lite venv for backend and orchestrator (no heavy AI packages).
    const liteVenvPython = path.join(
      process.resourcesPath,
      "lite-venv",
      "Scripts",
      "python.exe"
    );
    let orchestratorPython = pythonExecutable; // fallback to system
    try {
      require("fs").accessSync(liteVenvPython);
      orchestratorPython = liteVenvPython;
    } catch (_) {}

    // --- Start backend processes ---
    backendManager.startAll({
      pythonExecutable,
      sfPythonExecutable,
      orchestratorPythonExecutable: orchestratorPython,
      workDir,
      extraEnv: {
        // Override hardcoded DB paths so both processes use userData.
        MEMORY_DB_PATH: memoryDbPath,
        SF_RECOMMENDATIONS_DB_PATH: sfDbPath,
      },
    });

    // --- Open the window immediately (shows background color while backend warms up) ---
    createWindow();

    // --- Wait for the health endpoint ---
    try {
      await startupCheck.waitForBackend(30000);
    } catch (err) {
      // Backend did not start in time — warn but keep the window open.
      dialog.showErrorBox(
        "Recall — Backend startup timeout",
        "The Python backend did not respond within 30 seconds.\n\n" +
          err.message +
          "\n\nCheck logs at: " +
          path.join(app.getPath("userData"), "logs")
      );
      // Do NOT quit — the window stays open; some features may degrade.
    }
  } else {
    // Dev mode: Vite dev server is already running, just open the window.
    createWindow();
  }

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

// Stop all Python processes before the app exits.
// Uses app.on (not app.once) + a re-entry guard so the handler is not
// consumed on first fire — on macOS, app.exit(0) re-emits before-quit and
// a once-listener would leave the app hanging with no handler the second time.
let _quitting = false;
app.on("before-quit", (event) => {
  if (!isDev && backendManager && !_quitting) {
    _quitting = true;
    event.preventDefault();
    backendManager.stopAll().then(() => app.exit(0));
  }
});
