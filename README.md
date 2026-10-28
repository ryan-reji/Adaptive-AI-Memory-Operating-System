# Adaptive AI Memory Operating System

A privacy-preserving personal memory assistant. It captures permitted user activity, decides what is worth remembering, stores it as long-term memory, and makes it searchable through RAG.

## Features

- File, browser, and VS Code activity monitoring
- AI-based relevance classification (local Ollama, `qwen3.5:4b`)
- Relevance-aware memory creation, stored in SQLite
- Embedding and chunking into ChromaDB for semantic retrieval
- RAG-based question answering over memories
- Smart Forgetting: Random Forest-based file-retention recommendations with local LLM fallback for low-confidence predictions
- Independent Smart Forgetting background runner: performs an initial scan and reassesses the known file inventory every 12 hours
- Privacy controls: allow-all / allow-only modes, folder exclusions
- Desktop UI (Electron + React) wired to the live backend

The architecture is modular: monitoring, memory management, AI processing, Smart Forgetting, and the UI are independent components.

## Architecture

```text
USER
  |
python -m memory.orchestrator
  |
File + Browser + VS Code monitoring
  |
activity_evidence (SQLite)
  |
Every 60 seconds: LLM relevance classification (Ollama)
  |
relevance_decisions
  |
memory_records (SQLite)
  |
Embedding + chunking -> ChromaDB
  |
ai_processed = true
  |
FastAPI backend (backend/app) <- Desktop UI (ui/)


INDEPENDENT SMART FORGETTING SERVICE
  |
python -m memory.smart_forgetting.runner
  |
Initial scan on first run
  |
Reassess known file inventory every 12 hours
  |
Extract file metadata and activity features
  |
Random Forest classification
  |
Low-confidence predictions -> Ollama LLM fallback
  |
Recommendations (SQLite)
  |
keep / review
```

## Team

| Member | Owns |
|---|---|
| 1 | Embeddings, ChromaDB, RAG, local Ollama LLM |
| 2 | Activity monitoring, relevance pipeline, memory lifecycle, Smart Forgetting |
| 3 | Desktop app (`ui/`): Electron + React frontend |
| 4 | Backend/API layer (`backend/app`): connects the UI to Members 1 and 2's modules |

## Getting Started

Five processes run at the same time, each in its own terminal: the capture pipeline, backend API, desktop app, ChromaDB, and Smart Forgetting runner.

### Prerequisites

- Python 3.11+
- Node.js + npm
- [Ollama](https://ollama.com/download) with the model pulled:

```bash
ollama pull qwen3.5:4b
```

### Python environment

From the repo root:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Terminal 1: capture pipeline

```powershell
.\venv\Scripts\Activate.ps1; python -m memory.orchestrator
```

### Terminal 2: API server

```powershell
.\venv\Scripts\Activate.ps1; uvicorn backend.app.main:app --reload --port 8000
```

### Terminal 3: desktop app

```powershell
cd ui; npm run electron:dev
```

### Terminal 4: ChromaDB — Vector Database

```powershell
chroma run --path ".\memory\ai_engine\chroma_db" --host 127.0.0.1 --port 8001
```

### Terminal 5: Smart Forgetting — Background Runner

Smart Forgetting uses its dedicated Python environment to maintain compatibility with the trained model.

```powershell
.\.venv_smart_forgetting\Scripts\python.exe -m memory.smart_forgetting.runner
```

The runner performs an initial scan, then reassesses the known file inventory every 12 hours. Keep this terminal running. It resumes based on the last successful scan timestamp after restarting.

Keep all five terminals running. Also ensure Ollama is running and `qwen3.5:4b` is available for AI responses.

**Mock mode:** set `VITE_USE_MOCK=true` (or delete `ui/.env`) to run the UI on mock data without the backend or Ollama. This is useful for frontend-only development or as a demo fallback.

### Packaging

```bash
cd ui
npm run electron:build
```

The installer is written to `ui/release/`.

## API Reference

Interactive docs are at `http://127.0.0.1:8000/docs` once the backend is running.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Health check |
| `GET /memories/` | List active memories (`limit`, `offset`) |
| `GET /memories/{id}` | Single memory |
| `GET /evidence/` | Raw captured evidence |
| `GET /evidence/{id}` | Single evidence record |
| `POST /query/` | RAG question answering (`query`, `top_k`) |
| `GET/PUT /permissions/mode` | `allow_all` / `allow_only` |
| `GET/POST/DELETE /permissions/exclusions` | Excluded folders |
| `GET/POST/DELETE /permissions/allowed-folders` | Allowed folders (`allow_only` mode) |
| `GET/POST/DELETE /permissions/project-folders` | Named project folder mappings |

Sensitive fields (`content`, `path`, `source_path`, etc.) are stripped from all API responses before they reach the frontend. There are no create/update/delete endpoints for memories or evidence.

Smart Forgetting currently runs independently and stores its recommendations in its own SQLite database. It is not exposed through the API in this version.

## Project Structure

```text
Adaptive-AI-Memory-Operating-System/
  backend/                  FastAPI app (Member 4)
    app/
      main.py
      api/routes/           health, memories, query, evidence, permissions
  memory/                   Members 1 and 2
    orchestrator.py
    capture/                file, browser, vscode monitors
    relevance/
    smart_forgetting/       Smart Forgetting model and background runner
      config.py
      feature_extractor.py
      model.py
      recommender.py
      safety.py
      pipeline.py
      runner.py
      recommendations.db   Generated at runtime
    ai_engine/              embeddings, ChromaDB, RAG
    database/
  ui/                       Electron + React app (Member 3)
    src/
      pages/                Dashboard, Search, Timeline, Settings
      components/
      lib/                  api.js, memoryAdapter.js, mockData.js
    electron/
  requirements.txt
  requirements-dev.txt
  smart_forgetting_rf.joblib
  .gitignore
```

## Known Issues and Gaps

- Smart Forgetting inventory limitation: V1 reassesses known file paths recorded in `activity_evidence`; it does not scan the entire computer for previously unobserved files.
- No browser permission control. Allowed folders and exclusions apply only to file and VS Code activity. There is no way to restrict which sites or domains the browser monitor captures.
- VS Code activity can be slow to appear. If VS Code memories are missing, check that the orchestrator log shows "VS Code monitor started", make sure you are actively editing, and allow at least one full 60-second processing cycle.
- CORS is not configured on the backend. The dev server avoids this by proxying through Vite, but a packaged or production build will need an equivalent solution.
