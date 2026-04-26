# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This App Does

**ChunkLab** is a sandbox for testing text chunking and regex-based metadata extraction strategies, primarily for RAG (Retrieval-Augmented Generation) pipelines. Users paste markdown text, configure chunk size/overlap and regex patterns, and see real-time chunking results with optional token counts from various LLM providers.

It runs as a **web app** (Vite dev server + FastAPI) or as a **standalone Electron desktop app** (PyInstaller backend + electron-builder).

## Commands

### Backend

```bash
# Install dependencies (from repo root)
pip install -r backend/requirements.txt

# Run dev server (listens on 127.0.0.1:8000)
python backend/main.py

# Run tests
pytest backend/tests/ -v

# Run tests with coverage
pytest backend/tests/ -v --cov=backend/services --cov=backend/routers

# Run a single test file
pytest backend/tests/test_chunker.py -v

# Linting
ruff check backend/
black --check backend/
mypy backend/ --ignore-missing-imports
```

### Frontend

```bash
cd frontend

npm install         # Install deps
npm run dev         # Dev server at http://localhost:5173
npm run build       # Production build to frontend/dist
npm run type-check  # TypeScript check (tsc --noEmit)
```

### Electron (Desktop App)

```bash
# From repo root
npm run build:frontend   # Build React app to frontend/dist
npm run build:backend    # Package backend to exe via PyInstaller
npm run dist             # Full Electron build (Windows NSIS installer)
npm start                # Launch Electron dev
```

## Architecture

### Request Flow

1. User types markdown → `useChunker` hook debounces 500ms → `POST /api/chunk`
2. Backend validates params → `chunker.chunk_text()` splits by fixed char size with overlap → `metadata_extractor` applies compiled regex per chunk
3. Response renders chunks in `ChunkGrid`; token counts are **on-demand** via `POST /api/tokenize`

### Backend (`backend/`)

- **`main.py`** — FastAPI app, CORS (all origins), loads `.env`, includes 4 routers
- **`routers/`** — Thin HTTP layer: `chunk.py`, `tokenize.py`, `regex.py`, `models.py`
- **`services/`** — All business logic:
  - `chunker.py` — Pure function, character-based fixed-size chunking with overlap
  - `tokenizer.py` — Async, multi-provider: tiktoken (OpenAI/OpenRouter/LM Studio), Ollama (real async HTTP), Gemini/Anthropic (mocked), fallback mock
  - `metadata_extractor.py` — Applies pre-compiled regex to each chunk; uses `group(1)` if capture groups present, else `group(0)`
- **`models/`** — Pydantic v2 request/response schemas (`requests.py`, `responses.py`)

### Frontend (`frontend/src/`)

- **`App.jsx`** — Top-level state container; passes state down to components via props
- **`hooks/`** — All stateful logic lives here; components are presentational
  - `useChunker` — Debounced fetch, race-condition safe via `requestIdRef`
  - `useRegexPatterns` — Manages patterns array, on-demand test per pattern
  - `useTokenization` — On-demand token estimation, tracks provider/model
- **`services/api.js`** — Axios client; detects Electron (`window.electronAPI`) to set base URL to `http://127.0.0.1:8000`, otherwise uses `VITE_API_BASE_URL` or empty string (dev proxy)
- **`constants/models.js`** — `PROVIDERS` array defining all LLM providers and their defaults

### Key Constraints

- Chunk overlap must be strictly less than chunk size (enforced in Pydantic and router)
- Max 500,000 chars per text input, max 10 regex patterns per request, max 1000 chars per pattern
- Regex test endpoint returns max 20 matches; sets `truncated: true` if more exist
- `MOCK_MODE=true` (default) forces character-based token estimation regardless of provider
- All `.py` files carry Apache 2.0 license headers — maintain this when adding new files

## Environment Variables (`.env`)

```
BACKEND_PORT=8000
MOCK_MODE=true                          # Set false to enable real tokenizers
OLLAMA_BASE_URL=http://localhost:11434
LM_STUDIO_BASE_URL=http://localhost:1234
OPENAI_API_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=
```

## CI/CD Workflows

| Workflow | Trigger | What It Runs |
|---|---|---|
| `test.yml` | push/PR to master | `pytest` + Codecov upload |
| `lint.yml` | push/PR to master | ruff, black, mypy (Python); tsc (frontend) |
| `security.yml` | push to master + weekly | bandit (`--exit-zero`), pip-audit, npm audit (`--audit-level=high`) |
| `dco.yml` | PR to master | DCO sign-off check (`Signed-off-by` in commits) |

`pip-audit` and `npm audit` **will fail the workflow** if vulnerabilities at high/critical severity are found — keep dependencies patched.
