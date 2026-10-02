// Mock data shaped to match the REAL backend contract — confirmed via
// GET /docs and live curl/Invoke-RestMethod tests against the actual
// FastAPI backend, not guesses.
//
// Note: the backend intentionally strips sensitive fields (content, path,
// source_path, old_path, raw, any *_path field) before sending memory/
// evidence data — so mock entries never include those either, to avoid
// training the UI to expect fields that will never actually arrive.

export const mockMemories = [
  {
    id: 143,
    evidence_id: 149,
    source_type: "browser",
    timestamp: "2026-09-19T14:15:09.800561",
    action: "viewed",
    duration_seconds: 231.38,
    details: {
      browser: "Chrome",
      title: "Adaptive AI Memory OS - Swagger UI - Google Chrome",
      sessions: 15,
      first_seen: "2026-09-19T14:09:08.962909",
      last_seen: "2026-09-19T14:15:09.800561",
    },
    created_at: "2026-09-19T14:15:09.805506",
    status: "active",
    ai_processed: true,
  },
  {
    id: 142,
    evidence_id: 148,
    source_type: "browser",
    timestamp: "2026-09-19T14:14:58.773948",
    action: "viewed",
    duration_seconds: 544.86,
    details: {
      browser: "Chrome",
      title: "Major project excellence strategy - Claude - Google Chrome",
      sessions: 53,
      first_seen: "2026-09-19T13:28:05.869289",
      last_seen: "2026-09-19T14:14:58.773948",
    },
    created_at: "2026-09-19T14:14:58.778632",
    status: "active",
    ai_processed: true,
  },
  {
    id: 90,
    evidence_id: 95,
    source_type: "vscode",
    timestamp: "2026-09-19T12:10:00.000000",
    action: "edited",
    duration_seconds: 300,
    details: {
      editor: "Visual Studio Code",
      project: "ai-memory-frontend",
      file: "SearchPage.jsx",
      sessions: 4,
    },
    created_at: "2026-09-19T12:10:00.000000",
    status: "active",
    ai_processed: true,
  },
  {
    id: 80,
    evidence_id: 85,
    source_type: "file",
    timestamp: "2026-09-19T11:00:00.000000",
    action: "modified",
    duration_seconds: 0,
    details: {
      file_name: "notes.txt",
      file_type: "text",
    },
    created_at: "2026-09-19T11:00:00.000000",
    status: "active",
    ai_processed: false,
  },
];

// Mimics POST /query/ — real endpoint returns a generated answer, not a
// list of matches, since it's RAG question-answering over ChromaDB.
export function mockAnswer(query, topK = 3) {
  const hit = mockMemories.find((m) =>
    JSON.stringify(m.details).toLowerCase().includes(query.toLowerCase())
  );
  return {
    query,
    answer: hit
      ? `Based on what's been captured, this relates to "${hit.details.title || hit.details.file || hit.details.file_name}" from ${hit.source_type}.`
      : `I don't have enough information in the retrieved context to answer your question about "${query}".`,
    retrieval_time_ms: 8 + Math.random() * 10,
  };
}

export const mockPermissionMode = { mode: "allow_all" };

// Kept as plain string arrays internally — api.js wraps these into the
// real API's {path} object shape when returning them in mock mode.
export const mockAllowedFolders = [];
export const mockExclusions = [];