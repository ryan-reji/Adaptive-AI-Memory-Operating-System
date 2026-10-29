// ui/electron/backend-manager.cjs
"use strict";

const { spawn, exec } = require("child_process");
const path = require("path");
const fs = require("fs");
const { app, dialog } = require("electron");

// Tracks all running child processes: [{ label, proc }]
const _procs = [];
// Set to true during intentional shutdown to suppress crash dialogs.
let _stopping = false;

/**
 * Ensure the logs directory exists and return a writable stream for a log file.
 * @param {string} name - Short name used as the log filename (no extension).
 * @returns {fs.WriteStream}
 */
function _logStream(name) {
  const logsDir = path.join(app.getPath("userData"), "logs");
  fs.mkdirSync(logsDir, { recursive: true });
  const logPath = path.join(logsDir, `${name}.log`);
  return fs.createWriteStream(logPath, { flags: "a" });
}

/**
 * Spawn a single Python process and wire up logging + crash detection.
 * @param {string}   label  - Human-readable name used for logs and dialogs.
 * @param {string[]} args   - Arguments to pass after the Python executable.
 * @param {{ pythonExecutable: string, workDir: string }} config
 */
function _spawnOne(label, args, config) {
  const { pythonExecutable, workDir } = config;

  const proc = spawn(pythonExecutable, args, {
    cwd: workDir,
    env: {
      ...process.env,
      // Make backend.* and memory.* importable as top-level packages.
      PYTHONPATH: workDir,
      // Disable Python's output buffering so log lines appear in real-time.
      PYTHONUNBUFFERED: "1",
    },
    stdio: ["ignore", "pipe", "pipe"],
  });

  const logStream = _logStream(label);
  const prefix = `[${label}]`;

  proc.stdout.on("data", (data) => {
    logStream.write(`${new Date().toISOString()} ${prefix} ${data}`);
  });

  proc.stderr.on("data", (data) => {
    logStream.write(`${new Date().toISOString()} ${prefix} [ERR] ${data}`);
  });

  proc.on("exit", (code, signal) => {
    logStream.write(
      `${new Date().toISOString()} ${prefix} exited — code=${code} signal=${signal}\n`
    );
    logStream.end();

    // Remove from tracked list.
    const idx = _procs.findIndex((e) => e.proc === proc);
    if (idx !== -1) _procs.splice(idx, 1);

    if (!_stopping) {
      dialog.showMessageBox({
        type: "warning",
        title: "Recall — Backend process stopped",
        message: `The "${label}" process exited unexpectedly (code ${code}).`,
        detail:
          "Some features may not work. Check logs for details.\n" +
          `Log: ${path.join(app.getPath("userData"), "logs", label + ".log")}`,
        buttons: ["OK"],
      });
    }
  });

  proc.on("error", (err) => {
    logStream.write(
      `${new Date().toISOString()} ${prefix} [SPAWN ERROR] ${err.message}\n`
    );
  });

  _procs.push({ label, proc });
  return proc;
}

/**
 * Kill a single process entry gracefully, with a forced kill fallback after 3 s.
 * Returns a Promise that resolves when the process has exited.
 * @param {{ label: string, proc: import("child_process").ChildProcess }} entry
 * @returns {Promise<void>}
 */
function _kill(entry) {
  return new Promise((resolve) => {
    const { label, proc } = entry;

    if (proc.exitCode !== null || proc.killed) {
      resolve();
      return;
    }

    // Force-kill fallback after 3 seconds.
    const timer = setTimeout(() => {
      try {
        if (process.platform === "win32") {
          exec(`taskkill /F /T /PID ${proc.pid}`, () => resolve());
        } else {
          proc.kill("SIGKILL");
          resolve();
        }
      } catch (_) {
        resolve();
      }
    }, 3000);

    proc.once("exit", () => {
      clearTimeout(timer);
      resolve();
    });

    // Attempt graceful termination first.
    try {
      if (process.platform === "win32") {
        process.kill(proc.pid, "SIGTERM");
      } else {
        proc.kill("SIGTERM");
      }
    } catch (_) {
      // Process may have already exited.
    }
  });
}

/**
 * Start all three backend processes.
 * @param {{ pythonExecutable: string, workDir: string }} config
 */
function startAll(config) {
  _stopping = false;

  _spawnOne(
    "backend",
    ["-m", "uvicorn", "backend.app.main:app", "--port", "8000"],
    config
  );
  _spawnOne("orchestrator", ["-m", "memory.orchestrator"], config);
  _spawnOne(
    "smart-forgetting",
    ["-m", "memory.smart_forgetting.runner"],
    config
  );
}

/**
 * Gracefully stop all tracked backend processes.
 * Resolves when all processes have exited (or after 4 seconds max total).
 * @returns {Promise<void>}
 */
function stopAll() {
  _stopping = true;
  const toKill = _procs.slice(); // snapshot before async mutations

  const killAll = Promise.all(toKill.map(_kill)).then(() => {
    _procs.length = 0;
  });

  // 4-second hard ceiling regardless of individual kill timeouts.
  const ceiling = new Promise((resolve) => setTimeout(resolve, 4000));

  return Promise.race([killAll, ceiling]);
}

module.exports = { startAll, stopAll };
