# Recall — Desktop Application (Member 3)

Electron + React desktop app for the Adaptive AI Memory OS project. Currently runs
entirely on mock data so it works before Members 1/2/4 have anything built.

## Screens

- **Dashboard** — overview, quick search, recent memories
- **Search** — the AI search box + explainable memory results (source, project, relevance %, kept/summarized/archived status)
- **Timeline** — day-by-day and by-project view of captured activity
- **Privacy & Settings** — capture toggle, per-source toggles, forgetting policy, sensitive-data filter

## Getting started

```bash
npm install

# Run in the browser (fastest for UI iteration)
npm run dev

# Run inside Electron (what the real app will look like)
npm run electron:dev

# Build a distributable installer
npm run electron:build
```

## Switching from mock data to the real backend

All data access goes through `src/lib/api.js`. Right now `USE_MOCK` defaults to
true. To point at Member 4's real FastAPI backend:

1. Create a `.env` file in the project root:
   ```
   VITE_USE_MOCK=false
   VITE_API_BASE=http://localhost:8000
   ```
2. Make sure the backend's response shapes match what's in `src/lib/mockData.js`.
   If field names differ, either ask Member 4 to match them, or adjust the
   `real*` functions in `api.js` to map the response.

**Confirm this contract with Member 4 as early as possible** — it's the only thing
blocking this app from being "real":

| Endpoint | Purpose |
|---|---|
| `GET /memories/search?q=` | AI search box results |
| `GET /memories/recent` | Dashboard recent activity |
| `GET /timeline` | Timeline page, by-day |
| `GET /projects` | Timeline page, by-project + dashboard stats |
| `GET /settings` / `POST /settings` | Privacy & Settings page |

Suggested memory object shape (already used by the mock data and UI):

```json
{
  "id": "m1",
  "text": "string",
  "source": "browser | pdf | vscode | files | email",
  "sourceLabel": "human-readable source, e.g. 'VS Code — app.py'",
  "project": "string",
  "timestamp": "ISO 8601 datetime",
  "importance": 0.0,
  "status": "kept | summarized | archived"
}
```

## Design notes

- Deep teal-ink background rather than pure black, warm amber "recall glow" accent
  for anything AI-surfaced (relevance %, highlighted states), sage/rust to signal
  kept vs. fading memories.
- The vertical line on the Timeline page ("memory thread") is the one signature
  visual element — its opacity increases with activity volume for that day, so it
  doubles as a data encoding, not just decoration.
- Fonts are system/web-safe on purpose (no Google Fonts import) so the app looks
  right offline, which matters for a local-first, privacy-focused product.

## Packaging notes

- Uses `HashRouter` (not `BrowserRouter`) because Electron loads the built app from
  a `file://` path, where a normal history router breaks on refresh/navigation.
- `vite.config.js` sets `base: './'` for the same reason — asset paths must be
  relative, not absolute, once bundled.
- Test the packaged build (`npm run electron:build`), not just `electron:dev` —
  packaging bugs (missing files, broken relative paths) only show up after
  packaging.
