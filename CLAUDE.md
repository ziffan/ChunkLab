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
  - `tokenizer.py` — Async, multi-provider: tiktoken (OpenAI/OpenRouter/LM Studio), Ollama (real async HTTP), Gemini (mocked), fallback mock
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

## Windows Terminal Gotchas (PowerShell 5.1)

These are real failures that happened during this project. Do not repeat them.

### 1. Heredoc `>` causes silent redirection failure

PowerShell 5.1 treats `>` as a redirection operator **inside heredoc commit messages**, even when the `>` appears inside a quoted string passed to a native executable like `git`.

**Symptom:** `git commit` exits with `error: pathspec '>' did not match any file(s)` — no actual commit is created.

**Example of broken commit message text:**
```
feat: add H1 > H2 header path metadata
```

**Fix:** Rephrase to avoid `>` entirely:
```
feat: add H1-to-H2 header path metadata
```

Never use `>` or `<` in git commit messages written via PowerShell heredoc (`@'...'@` or `@"..."@`).

### 2. `&&` is not available in PowerShell 5.1

`&&` is a pipeline chain operator that does **not exist** in Windows PowerShell 5.1 (only in PowerShell 7+).

**Fix:** Chain commands with `; if ($?) { ... }` or split into separate Bash tool calls.

### 3. Always use absolute paths for linting tools

When running `ruff`, `black`, `mypy`, `pytest` from PowerShell, always pass the **absolute path** to the target directory or file. Relative paths like `backend/` may silently fail or target the wrong directory depending on working directory state.

```powershell
# Correct
ruff check "D:\PROYEK\ChunkingSanbox\backend"
black --check "D:\PROYEK\ChunkingSanbox\backend"
pytest "D:\PROYEK\ChunkingSanbox\backend\tests" -v

# Avoid
ruff check backend/
```

### 4. Use the Bash tool (not PowerShell) for multi-step shell chains

For sequences like `cd frontend && npm run type-check`, use the **Bash tool** with POSIX syntax rather than the PowerShell tool. The Bash tool is available and avoids PowerShell operator pitfalls for these kinds of chains.

## Current Status (v2.1 — as of 2026-05-01)

All Phase 9 tasks are complete. 138 tests passing.

### legal_id PDF Artifact Handling

PDF-converted Indonesian legal documents frequently have malformed line structure. Three known issues and their fixes:

1. **Inline Pasal headers** — PDF converters merge `Pasal N` and content onto one line.
   Fixed via `_RE_PASAL = re.compile(r"^Pasal\s+(\d+[A-Z]?)(?:\s*$|\s+(?=[A-Z][a-z]))", _M)`.

2. **is_amendment false positive** — `_RE_AMENDMENT.search(text)` scans the full body, falsely triggering when PENJELASAN quotes an amendment UU. Fixed by scoping the search to the first line (document title) only.

3. **Mid-line section headers** — PENJELASAN ATAS and LAMPIRAN markers appear mid-line when PDF page breaks are not preserved as newlines. Fixed by `_normalize_pdf_lines()` preprocessing step in `_segment()`.

### Retrieval Timeout

`retrieveChunks()` in `frontend/src/services/api.js` uses a 120s timeout override (global axios default is 30s). The retrieval model (`intfloat/multilingual-e5-large`) warms up at startup via FastAPI `lifespan` context in `backend/main.py`.

## Roadmap (Optional Polish)

- **Docker compose** — single `docker compose up` to start both backend and frontend
- **Updated README screenshots** — replace placeholder screenshots with current UI
