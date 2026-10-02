# Adaptive-AI-Memory-Operating-System

Privacy-preserving AI Memory Assistant with activity capture, relevance-aware memory creation, smart forgetting, and information retrieval using RAG.

## Overview

The Adaptive AI Memory Operating System is a privacy-preserving personal memory assistant designed to continuously capture permitted user activity, identify information that may be useful as long-term memory, store it in a structured memory system, and make it available for semantic retrieval through RAG.

The system is designed around a modular architecture where activity monitoring, memory management, AI processing, and user interaction are separated into independent components.

The current system supports:

- File, Browser and VS Code activity monitoring
- Activity evidence collection and storage
- AI-based activity relevance classification
- Relevance-aware memory creation
- Persistent memory storage using SQLite
- Memory ingestion into ChromaDB
- Embedding generation
- RAG-based memory retrieval
- Privacy and permission controls (allow-all / allow-only modes, folder exclusions)
- Desktop UI (Electron + React) fully wired to the live backend

Smart Forgetting is part of the project architecture and is planned as a later memory-management component — memories are currently permanent once created.

## Architecture

USER
↓
python -m memory.orchestrator
↓
File + Browser + VS Code monitoring
↓
activity_evidence (SQLite)
↓
Every 60 seconds
↓
LLM relevance classification (Ollama, qwen3.5:4b)
↓
relevance_decisions
↓
memory_records (SQLite, permanent)
↓
Embedding + chunking → ChromaDB
↓
ai_processed = true
↓
FastAPI backend (backend/app) ← Desktop UI (ui/)


## Team & Responsibilities

| Member | Owns |
|---|---|
| 1 | Embeddings, ChromaDB, RAG, local Ollama LLM (`qwen3.5:4b`) |
| 2 | Activity monitoring (file/browser/VS Code), relevance pipeline, memory lifecycle, smart forgetting (not yet implemented) |
| 3 | Desktop application (`ui/`) — Electron + React frontend consuming the backend API |
| 4 | Backend/API layer (`backend/app`) — connects the UI to Members 1 & 2's modules |

## Getting Started

Requires three processes running simultaneously, in separate terminals: capture pipeline, backend API, and the desktop app.

### 1. Prerequisites

- Python (3.11+ recommended)
- Node.js + npm
- [Ollama](https://ollama.com/download) installed, with the model pulled:
```bash
  ollama pull qwen3.5:4b
```

### 2. Python environment (backend + capture pipeline)

From the repo root:
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Terminal 1** — capture pipeline (file/browser/VS Code monitoring + relevance + memory creation):
```bash
python -m memory.orchestrator
```

**Terminal 2** — API server:
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Desktop app

**Terminal 3**, from the repo root:
```bash
cd ui
npm install
```

Create `ui/.env`:

VITE_USE_MOCK=false
VITE_API_BASE=/api


```bash
npm run electron:dev
```

The UI proxies `/api` to `http://127.0.0.1:8000` (see `ui/vite.config.js`), since the backend doesn't currently have CORS configured for direct cross-origin requests.

Set `VITE_USE_MOCK=true` (or delete `ui/.env`) to run the UI against realistic mock data without the backend/Ollama running — useful for frontend-only development or as a demo fallback if live capture is unreliable.

### Packaging the desktop app

```bash
cd ui
npm run electron:build
```
Produces a distributable installer in `ui/release/`.

## API Reference

Full interactive docs available at `http://127.0.0.1:8000/docs` once the backend is running. Summary:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Health check |
| `GET /memories/` | List active memories (`limit`, `offset`) |
| `GET /memories/{id}` | Single memory |
| `GET /evidence/` | Raw captured evidence |
| `GET /evidence/{id}` | Single evidence record |
| `POST /query/` | RAG question answering (`query`, `top_k`) |
| `GET/PUT /permissions/mode` | `allow_all` / `allow_only` |
| `GET/POST/DELETE /permissions/exclusions` | Excluded
Claude’s response was interrupted.

no spcing just easy to copy paste

markdown
# Adaptive-AI-Memory-Operating-System

Privacy-preserving AI Memory Assistant with activity capture, relevance-aware memory creation, smart forgetting, and information retrieval using RAG.

## Overview

The Adaptive AI Memory Operating System is a privacy-preserving personal memory assistant designed to continuously capture permitted user activity, identify information that may be useful as long-term memory, store it in a structured memory system, and make it available for semantic retrieval through RAG.

The system is designed around a modular architecture where activity monitoring, memory management, AI processing, and user interaction are separated into independent components.

The current system supports:

- File, Browser and VS Code activity monitoring
- Activity evidence collection and storage
- AI-based activity relevance classification
- Relevance-aware memory creation
- Persistent memory storage using SQLite
- Memory ingestion into ChromaDB
- Embedding generation
- RAG-based memory retrieval
- Privacy and permission controls (allow-all / allow-only modes, folder exclusions)
- Desktop UI (Electron + React) fully wired to the live backend

Smart Forgetting is part of the project architecture and is planned as a later memory-management component — memories are currently permanent once created.

## Architecture

USER
|
v
python -m memory.orchestrator
|
v
File + Browser + VS Code monitoring
|
v
activity_evidence (SQLite)
|
v
Every 60 seconds
|
v
LLM relevance classification (Ollama, qwen3.5:4b)
|
v
relevance_decisions
|
v
memory_records (SQLite, permanent)
|
v
Embedding + chunking -> ChromaDB
|
v
ai_processed = true
|
v
FastAPI backend (backend/app) <- Desktop UI (ui/)


## Team & Responsibilities

| Member | Owns |
|---|---|
| 1 | Embeddings, ChromaDB, RAG, local Ollama LLM (qwen3.5:4b) |
| 2 | Activity monitoring (file/browser/VS Code), relevance pipeline, memory lifecycle, smart forgetting (not yet implemented) |
| 3 | Desktop application (ui/) - Electron + React frontend consuming the backend API |
| 4 | Backend/API layer (backend/app) - connects the UI to Members 1 & 2's modules |

## Getting Started

Requires three processes running simultaneously, in separate terminals: capture pipeline, backend API, and the desktop app.

### 1. Prerequisites

- Python (3.11+ recommended)
- Node.js + npm
- Ollama installed (https://ollama.com/download), with the model pulled:

```bash
ollama pull qwen3.5:4b
```

### 2. Python environment (backend + capture pipeline)

From the repo root:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Terminal 1 - capture pipeline (file/browser/VS Code monitoring + relevance + memory creation):

```bash
python -m memory.orchestrator
```

Terminal 2 - API server:

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Desktop app

Terminal 3, from the repo root:

```bash
cd ui
npm install
```

Create ui/.env:

VITE_USE_MOCK=false
VITE_API_BASE=/api


```bash
npm run electron:dev
```

The UI proxies /api to http://127.0.0.1:8000 (see ui/vite.config.js), since the backend doesn't currently have CORS configured for direct cross-origin requests.

Set VITE_USE_MOCK=true (or delete ui/.env) to run the UI against realistic mock data without the backend/Ollama running - useful for frontend-only development or as a demo fallback if live capture is unreliable.

### Packaging the desktop app

```bash
cd ui
npm run electron:build
```

Produces a distributable installer in ui/release/.

## API Reference

Full interactive docs available at http://127.0.0.1:8000/docs once the backend is running. Summary:

| Endpoint | Purpose |
|---|---|
| GET /health | Health check |
| GET /memories/ | List active memories (limit, offset) |
| GET /memories/{id} | Single memory |
| GET /evidence/ | Raw captured evidence |
| GET /evidence/{id} | Single evidence record |
| POST /query/ | RAG question answering (query, top_k) |
| GET/PUT /permissions/mode | allow_all / allow_only |
| GET/POST/DELETE /permissions/exclusions | Excluded folders |
| GET/POST/DELETE /permissions/allowed-folders | Allowed folders (used in allow_only mode) |
| GET/POST/DELETE /permissions/project-folders | Named project folder mappings |

There are currently no memory/evidence mutation APIs (no create/update/delete) - memories are permanent until Smart Forgetting is implemented.

Sensitive fields (content, path, source_path, etc.) are intentionally stripped from all API responses before reaching the frontend.

## Project Structure

Adaptive-AI-Memory-Operating-System/
backend/ - Member 4: FastAPI app
app/
main.py
api/routes/ (health, memories, query, evidence, permissions)
memory/ - Member 1 & 2
orchestrator.py
capture/ (file, browser, vscode monitors)
relevance/
ai_engine/ (embeddings, ChromaDB, RAG)
database/
ui/ - Member 3: Electron + React desktop app
src/
pages/ (Dashboard, Search, Timeline, Settings)
components/
lib/ (api.js, memoryAdapter.js, mockData.js)
electron/
requirements.txt
requirements-dev.txt
.gitignore


## Known Issues / Gaps

- Smart Forgetting is not implemented - no memory deletion/expiry exists yet; all memories are permanent
- Browser permission control does not exist - allowed-folders/exclusions apply to file and VS Code activity only; there is currently no way to restrict which sites/domains the browser monitor captures
- VS Code activity can take noticeably longer to register than browser activity in testing - if VS Code memories aren't appearing, confirm the monitor is actually running (check orchestrator startup log for "VS Code monitor started") and that you're actively editing, then allow at least one full 60-second processing cycle
- CORS is not configured on the backend - the frontend dev server proxies API requests through Vite to avoid this; a packaged/production build will need an equivalent solution