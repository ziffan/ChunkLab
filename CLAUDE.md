# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

### 5. Node.js v24+ requires `--use-system-ca` on Windows with corporate proxy

Node.js v24 no longer uses the Windows system certificate store by default. On machines with SSL inspection / corporate CA, all `npm install` / `npm audit` calls will fail with `UNABLE_TO_VERIFY_LEAF_SIGNATURE`.

**Fix (already applied):** `NODE_OPTIONS=--use-system-ca` is set as a permanent Windows user environment variable. For PowerShell tool calls, set it in the session:
```powershell
$env:NODE_OPTIONS = "--use-system-ca"; npm install ...
```
For Bash tool calls, prefix the command:
```bash
NODE_OPTIONS=--use-system-ca npm install ...
```
`npm audit fix` also hits the SSL endpoint — same fix applies.

## Current Status (v0.2.2 — as of 2026-07-26)

Phase 1–3 cleanup complete (CI hardening, Electron removal, SentenceChunker merged into sentence_id, docs restructured). 137 tests passing (127 locally — 10 `TestTokenAwareChunker` skipped due to SSL/tiktoken download issue on corporate network; all pass in CI). Docker Compose support added. Retrieval tested end-to-end in Docker.

### Dependency Security Patches (2026-07-26)

- `mistune` bumped `3.0.2 → 3.3.4` (fixes CVE-2026-33079, CVE-2026-44897, plus 19 CVEs fixed in 3.3.0: CVE-2026-59922–59930, CVE-2026-44708, CVE-2026-44896, and 7 more — all previously unfixed CVEs now resolved)
- `axios` bumped `1.15.0 → 1.16.0` (fixes 13 high-severity CVEs)

### mypy Fix (2026-07-26)

`markdown_struct.py:45` — mistune 3.3.4 exposes explicit return type `str | list[...]` for `md(text)`. Fixed by replacing `if not ast_nodes` with `if not isinstance(ast_nodes, list) or not ast_nodes`, which narrows the type and satisfies mypy. (Originally applied for 3.2.1, still valid for 3.3.x.)

### legal_id PDF Artifact Handling

PDF-converted Indonesian legal documents frequently have malformed line structure. Three known issues and their fixes:

1. **Inline Pasal headers** — PDF converters merge `Pasal N` and content onto one line.
   Fixed via `_RE_PASAL = re.compile(r"^Pasal\s+(\d+[A-Z]?)(?:\s*$|\s+(?=[A-Z][a-z]))", _M)`.

2. **is_amendment false positive** — `_RE_AMENDMENT.search(text)` scans the full body, falsely triggering when PENJELASAN quotes an amendment UU. Fixed by scoping the search to the first line (document title) only.

3. **Mid-line section headers** — PENJELASAN ATAS and LAMPIRAN markers appear mid-line when PDF page breaks are not preserved as newlines. Fixed by `_normalize_pdf_lines()` preprocessing step in `_segment()`.

### Retrieval Timeout

`retrieveChunks()` in `frontend/src/services/api.js` uses a 120s timeout override (global axios default is 30s). The retrieval model (`intfloat/multilingual-e5-large`) warms up at startup via FastAPI `lifespan` context in `backend/main.py`.

## Docker

`docker compose up --build` starts both services. Relevant files: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`.

**Host networking:** `OLLAMA_BASE_URL` and `LM_STUDIO_BASE_URL` are overridden to `http://host.docker.internal:{port}` in `docker-compose.yml` so the backend container can reach Ollama/LM Studio running on the host. `extra_hosts: host-gateway` ensures this works on Linux too.
