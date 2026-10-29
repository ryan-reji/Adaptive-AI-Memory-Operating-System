// ui/electron/startup-check.cjs
"use strict";

const http = require("http");

const POLL_INTERVAL_MS = 1000;

/**
 * Performs a single HTTP GET to /health.
 * Resolves with true if the response is 2xx; false on any error or non-2xx.
 * Silently absorbs ECONNREFUSED, ENOTFOUND, and timeout errors.
 * @returns {Promise<boolean>}
 */
function _poll() {
  return new Promise((resolve) => {
    const req = http.get(
      "http://localhost:8000/health",
      { timeout: 2000 },
      (res) => {
        // Drain the response body so the socket is released.
        res.resume();
        // Any 2xx is considered "ready".
        resolve(res.statusCode >= 200 && res.statusCode < 300);
      }
    );

    // ECONNREFUSED (not yet up), ENOTFOUND, or any other error → keep polling.
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * Polls http://localhost:8000/health every second until the backend responds
 * with a 2xx status or the timeout elapses.
 *
 * @param {number} [timeoutMs=30000] - Maximum time to wait in milliseconds.
 * @returns {Promise<void>} Resolves when ready; rejects with Error on timeout.
 */
function waitForBackend(timeoutMs = 30000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;

    async function attempt() {
      if (await _poll()) {
        resolve();
        return;
      }

      const remaining = deadline - Date.now();
      if (remaining <= POLL_INTERVAL_MS) {
        reject(
          new Error(
            `Backend did not become ready within ${timeoutMs / 1000} seconds. ` +
              "Check logs for Python process errors."
          )
        );
        return;
      }

      setTimeout(attempt, POLL_INTERVAL_MS);
    }

    attempt();
  });
}

module.exports = { waitForBackend };
