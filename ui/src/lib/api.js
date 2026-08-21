// Central place that talks to Member 4's FastAPI backend.
// While the backend is being built, USE_MOCK keeps the whole app fully working
// on fake data. Flip it to false (or set VITE_USE_MOCK=false in a .env file)
// once the real endpoints exist — nothing else in the app needs to change,
// as long as the response shapes match what's mocked in mockData.js.

import {
  mockMemories,
  mockTimeline,
  mockProjects,
  mockSettings,
  mockSearch,
  mockForget,
} from "./mockData";

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Small helper to simulate real network latency in mock mode so loading
// states are actually visible and tested during development.
function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function realFetch(path, options) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json();
}

export async function searchMemories(query) {
  if (USE_MOCK) {
    await delay(400);
    return mockSearch(query);
  }
  return realFetch(`/memories/search?q=${encodeURIComponent(query)}`);
}

export async function getRecentMemories() {
  if (USE_MOCK) {
    await delay(300);
    return mockMemories;
  }
  return realFetch("/memories/recent");
}

export async function getTimeline() {
  if (USE_MOCK) {
    await delay(300);
    return mockTimeline;
  }
  return realFetch("/timeline");
}

export async function getProjects() {
  if (USE_MOCK) {
    await delay(300);
    return mockProjects;
  }
  return realFetch("/projects");
}

export async function getSettings() {
  if (USE_MOCK) {
    await delay(200);
    return mockSettings;
  }
  return realFetch("/settings");
}

export async function updateSettings(newSettings) {
  if (USE_MOCK) {
    await delay(300);
    return { ...mockSettings, ...newSettings };
  }
  return realFetch("/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newSettings),
  });
}

export async function forgetMemory(id) {
  if (USE_MOCK) {
    await delay(250);
    return mockForget(id);
  }
  return realFetch(`/memories/${id}`, { method: "DELETE" });
}

export const isMockMode = USE_MOCK;
