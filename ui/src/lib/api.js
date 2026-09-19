import {
  mockMemories,
  mockAnswer,
  mockPermissionMode,
  mockAllowedFolders,
  mockExclusions,
} from "./mockData";

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
const API_BASE = import.meta.env.VITE_API_BASE || "/api";

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

class BackendError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function realFetch(path, options) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (res.status === 204) return null; // deletes return no body — never call .json() on these
  if (!res.ok) {
    // Never surface raw backend exception details to the user.
    if (res.status === 503) throw new BackendError(503, "AI engine is unavailable right now.");
    if (res.status === 404) throw new BackendError(404, "Not found.");
    throw new BackendError(res.status, "Something went wrong talking to the backend.");
  }
  return res.json();
}

// ---- Memories ----
export async function getMemories(limit = 50, offset = 0) {
  if (USE_MOCK) {
    await delay(300);
    return mockMemories.slice(offset, offset + limit);
  }
  return realFetch(`/memories/?limit=${limit}&offset=${offset}`);
}

export async function getMemory(id) {
  if (USE_MOCK) {
    await delay(150);
    return mockMemories.find((m) => m.id === id) || null;
  }
  return realFetch(`/memories/${id}`);
}

// ---- Evidence (not yet wired to any screen, available if needed) ----
export async function getEvidence(limit = 50, offset = 0) {
  if (USE_MOCK) {
    await delay(300);
    return [];
  }
  return realFetch(`/evidence/?limit=${limit}&offset=${offset}`);
}

// ---- AI / RAG query ----
export async function askQuery(query, topK = 3) {
  if (USE_MOCK) {
    await delay(500);
    return mockAnswer(query);
  }
  return realFetch(`/query/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
}

// ---- Permission mode ----
export async function getPermissionMode() {
  if (USE_MOCK) {
    await delay(150);
    return mockPermissionMode;
  }
  return realFetch(`/permissions/mode`);
}

export async function setPermissionMode(mode) {
  if (USE_MOCK) {
    await delay(200);
    mockPermissionMode.mode = mode;
    return mockPermissionMode;
  }
  return realFetch(`/permissions/mode`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
}

// ---- Allowed folders ----
export async function getAllowedFolders() {
  if (USE_MOCK) {
    await delay(150);
    return mockAllowedFolders.map((path) => ({ path }));
  }
  return realFetch(`/permissions/allowed-folders`);
}

export async function addAllowedFolder(path) {
  if (USE_MOCK) {
    await delay(200);
    mockAllowedFolders.push(path);
    return { path };
  }
  return realFetch(`/permissions/allowed-folders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
}

export async function removeAllowedFolder(path) {
  if (USE_MOCK) {
    await delay(200);
    const idx = mockAllowedFolders.indexOf(path);
    if (idx !== -1) mockAllowedFolders.splice(idx, 1);
    return null;
  }
  return realFetch(`/permissions/allowed-folders?path=${encodeURIComponent(path)}`, {
    method: "DELETE",
  });
}

// ---- Exclusions ----
export async function getExclusions() {
  if (USE_MOCK) {
    await delay(150);
    return mockExclusions.map((path) => ({ path }));
  }
  return realFetch(`/permissions/exclusions`);
}

export async function addExclusion(path) {
  if (USE_MOCK) {
    await delay(200);
    mockExclusions.push(path);
    return { path };
  }
  return realFetch(`/permissions/exclusions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
}

export async function removeExclusion(path) {
  if (USE_MOCK) {
    await delay(200);
    const idx = mockExclusions.indexOf(path);
    if (idx !== -1) mockExclusions.splice(idx, 1);
    return null;
  }
  return realFetch(`/permissions/exclusions?path=${encodeURIComponent(path)}`, {
    method: "DELETE",
  });
}

// ---- Project folders (API wired, no UI yet) ----
export async function getProjectFolders() {
  if (USE_MOCK) {
    await delay(150);
    return [];
  }
  return realFetch(`/permissions/project-folders`);
}

export async function addProjectFolder(path, projectName) {
  if (USE_MOCK) {
    await delay(200);
    return { path, project_name: projectName };
  }
  return realFetch(`/permissions/project-folders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, project_name: projectName }),
  });
}

export async function removeProjectFolder(path) {
  if (USE_MOCK) {
    await delay(200);
    return null;
  }
  return realFetch(`/permissions/project-folders?path=${encodeURIComponent(path)}`, {
    method: "DELETE",
  });
}

export const isMockMode = USE_MOCK;