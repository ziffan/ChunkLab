# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. It covers permanent working guidance (commands, architecture, constraints). Status, decisions, gotchas, and issues change more often and live in `docs/` instead — read them at session start:

- `docs/CONTEXT.md` — current status, what's in progress, next steps (top entry = where we are)
- `docs/DECISIONS.md` — locked / pending / never structural decisions
- `docs/GOTCHAS.md` — known traps in this codebase and tooling, don't repeat them
- `docs/ISSUES.md` — open and closed issues
- `CHANGELOG.md` — user-facing release notes (Keep a Changelog format)

## What This App Does

**ChunkLab** is a sandbox for testing text chunking and regex-based metadata extraction strategies, primarily for RAG (Retrieval-Augmented Generation) pipelines. Users paste markdown text, configure chunk size/overlap and regex patterns, and see real-time chunking results with optional token counts from various LLM providers.

It runs as a **web app** (Vite dev server + FastAPI) or via **Docker Compose** (`docker compose up --build`).

## Commands

### Backend

```bash
# Install dependencies (from repo root)
pip install -r backend/requirements.txt

# Run dev server (listens on 127.0.0.1:8000)
python -m backend.main

# Run tests
pytest backend/tests/ -v

# Run tests with coverage
pytest backend/tests/ -v --cov=backend/services --cov=backend/routers

# Run a single test file
pytest backend/tests/test_chunker.py -v

# Linting
ruff check backend/
black --check backend/
mypy backend/ --ignore-missing-imports --explicit-package-bases
```

### Frontend

```bash
cd frontend

npm install         # Install deps
npm run dev         # Dev server at http://localhost:5173
npm run build       # Production build to frontend/dist
npm run type-check  # TypeScript check (tsc --noEmit)
```

## Architecture

### Request Flow

1. User types markdown → `useChunker` hook debounces 500ms → `POST /api/chunk`
2. Backend validates params → `chunker.chunk_text()` dispatches to the selected strategy (6 total) → `metadata_extractor` applies compiled regex per chunk
3. Response renders chunks in `ChunkGrid`; token counts are **on-demand** via `POST /api/tokenize`

### Backend (`backend/`)

- **`main.py`** — FastAPI app, CORS (configurable via `FRONTEND_ORIGIN` env, default `localhost:5173`), loads `.env`, includes 4 routers
- **`routers/`** — Thin HTTP layer: `chunk.py`, `tokenize.py`, `regex.py`, `models.py`, `retrieve.py`
- **`services/`** — All business logic:
  - `chunker.py` — Dispatcher: `chunk_text()` and `chunk_by_strategy()`; delegates to one of 6 strategy classes in `services/chunkers/`
  - `retriever.py` — Singleton lazy-load of sentence-transformer model; cosine similarity top-K ranking
  - `tokenizer.py` — Async, multi-provider: tiktoken (OpenAI/OpenRouter/LM Studio), Ollama (real async HTTP), Gemini (mocked), fallback mock
  - `metadata_extractor.py` — Applies pre-compiled regex to each chunk; uses `group(1)` if capture groups present, else `group(0)`
- **`models/`** — Pydantic v2 request/response schemas (`requests.py`, `responses.py`)

### Frontend (`frontend/src/`)

- **`App.jsx`** — Top-level state container; passes state down to components via props
- **`hooks/`** — All stateful logic lives here; components are presentational
  - `useChunker` — Debounced fetch, race-condition safe via `requestIdRef`
  - `useRegexPatterns` — Manages patterns array, on-demand test per pattern
  - `useTokenization` — On-demand token estimation, tracks provider/model
- **`services/api.js`** — Axios client; uses `VITE_API_BASE_URL` or empty string (dev proxy via Vite)
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
RETRIEVAL_MODEL=intfloat/multilingual-e5-large  # Override embedding model for Retrieval Simulation
```

## CI/CD Workflows

| Workflow | Trigger | What It Runs |
|---|---|---|
| `test.yml` | push/PR to master | `pytest` + Codecov upload |
| `lint.yml` | push/PR to master | ruff, black, mypy (Python); tsc (frontend) |
| `security.yml` | push to master + weekly | bandit (`-lll`, excl. .venv), pip-audit, npm audit (`--audit-level=high`) |
| `dco.yml` | PR to master | DCO sign-off check (`Signed-off-by` in commits) |

`pip-audit` and `npm audit` **will fail the workflow** if vulnerabilities at high/critical severity are found — keep dependencies patched.

## Docker

`docker compose up --build` starts both services. Relevant files: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`.

**Host networking:** `OLLAMA_BASE_URL` and `LM_STUDIO_BASE_URL` are overridden to `http://host.docker.internal:{port}` in `docker-compose.yml` so the backend container can reach Ollama/LM Studio running on the host. `extra_hosts: host-gateway` ensures this works on Linux too.
