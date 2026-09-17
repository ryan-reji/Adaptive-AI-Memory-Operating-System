const { contextBridge } = require("electron");

// Placeholder bridge. If Member 4's backend ever needs to be spawned as a
// local child process (instead of just being fetched over HTTP), expose
// those controls here via contextBridge rather than turning on
// nodeIntegration in the renderer.
contextBridge.exposeInMainWorld("recallApp", {
  version: process.versions.electron,
});
