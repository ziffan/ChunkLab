# Changelog

All notable changes to ChunkLab will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — v2.0.0

### Added
- `.progress` tracker file as single source of truth for v2 implementation progress (Phase 0.1)
- `MockBanner` component: permanent warning banner shown when `MOCK_MODE=true` (Phase 0.4)
- `GET /api/health` now returns `mock_mode: bool` field (Phase 0.4)
- `backend/services/chunkers/` package: `BaseChunker` abstract class, `FixedSizeChunker`, `CHUNKER_REGISTRY` — foundation for multiple chunking strategies (Phase 1.1)
- `chunk_by_strategy(text, strategy, **params)` dispatcher in `chunker.py` for strategy-based routing (Phase 1.1)
- `RecursiveCharacterChunker`: splits by `\n\n` → `\n` → `. ` → ` ` → char, respects paragraph boundaries, two-phase trim guarantees hard `chunk_size` limit (Phase 1.2)
- `TokenAwareChunker`: encode → slice by exact token count → decode using tiktoken; params `chunk_size_tokens`, `chunk_overlap_tokens`, `encoding_name` (default `cl100k_base`); guaranteed hard token limit (Phase 1.3)
- `SentenceChunker`: groups sentences via pysbd; params `language`, `max_sentences_per_chunk`, `chunk_overlap_sentences`; every chunk ends at sentence boundary (Phase 1.4)
- `pysbd==0.3.4` added to `requirements.txt` (Phase 1.4)
- `MarkdownStructureChunker`: splits by mistune 3.x AST header boundaries; params `header_level` (default 2), `max_chunk_size` (default 2000); oversized sections sub-split by characters with header preserved; no overlap (structure-based) (Phase 1.5)
- `strategy_markdown.json` test fixture with happy_path, edge_no_headers, edge_h1_only, edge_oversized cases (Phase 1.5)
- `ChunkRequest` schema: `strategy` field (default `"fixed"`, backward-compatible) and `strategy_params: dict` for per-strategy parameters (Phase 1.6)
- `/api/chunk` router dispatches to `chunk_by_strategy()` for non-fixed strategies; returns `INVALID_PARAMETERS` error for unknown strategy or bad params (Phase 1.6)

### Fixed
- `/api/chunk` now forwards `chunk_size` and `chunk_overlap` to `RecursiveCharacterChunker` via `strategy_params.setdefault()` so top-level params are respected (Phase 1.8)
- `StrategySelector` component: strategy dropdown with per-strategy param controls — separators (recursive), chunk_size_tokens / chunk_overlap_tokens / encoding_name (token), language / max_sentences_per_chunk / chunk_overlap_sentences (sentence), header_level / max_chunk_size (markdown) (Phase 1.7)
- `useChunker` hook extended to pass `strategy` and `strategy_params` to `/api/chunk`; chunk_size + chunk_overlap forwarded for fixed/recursive strategies (Phase 1.7)
- `ParameterPanel` hides chunk_size/overlap sliders when strategy is not fixed or recursive (Phase 1.7)
- `api_strategies.json` fixture with integration test cases for all 5 strategies (Phase 1.8)
- 5 new API integration tests in `test_api.py`: recursive, token, sentence, markdown structure, and invalid strategy (→ 422) (Phase 1.8)
- `FileUploader` component: drag-and-drop zone + click-to-browse for `.txt` / `.md` files; validates extension; rejects files > 500 KB; shows filename badge with × clear button; friendly error for unsupported formats (Phase 2.1–2.4)
- `useFileUpload` hook: encapsulates FileReader logic, extension + size validation, filename state (Phase 2.2)
- `quality_metrics.py`: `boundary_quality` (0–1 score for sentence-end + boundary-start), `information_density` (non-whitespace ratio), `is_complete` (mid-word cut detection) (Phase 3.1–3.3)
- `ChunkData` schema extended with `boundary_quality: float`, `information_density: float`, `is_complete: bool` (default values preserve backward compat) (Phase 3.4)
- `QualityBadge` component: colored dot (🟢/🟡/🔴 per boundary_quality threshold) + BQ% / ID% display + truncation warning when `is_complete=false` (Phase 3.5)
- `test_quality_metrics.py`: 24 tests covering all three metrics, happy path + edge cases (Phase 3.6)
- `requirements-retrieval.txt`: optional extras file for `sentence-transformers>=2.7.0` + `numpy>=1.24` — not in main requirements (Phase 4.1)
- `retriever.py`: singleton lazy-load `all-MiniLM-L6-v2`; `retrieve()` computes cosine similarity via `st_util.cos_sim`, returns top-K ranked results (Phase 4.2, 4.4)
- `POST /api/retrieve`: accepts `query`, `chunks[]`, `top_k`; returns ranked results with scores; returns 503 with `RETRIEVAL_UNAVAILABLE` when extras not installed (Phase 4.3, 4.5)
- `RetrievalPanel` component: query input + Retrieve button; score bar per result; install hint when 503 (Phase 4.6)
- `useRetrieval` hook: manages query state, results, loading, and 503 detection (Phase 4.6)
- `test_retriever.py`: 7 tests with mocked embedder covering 503 degrade + happy path + schema + sort order (Phase 4.7)
- `useComparison` hook: two parallel `useConfigChunker` instances, fires two simultaneous `/api/chunk` calls with independent configs (Phase 5.2)
- `ComparisonView` component: dual-pane layout, each pane has independent `StrategySelector` + `ParameterPanel` + `ChunkGrid`; Config A in indigo, Config B in amber (Phase 5.1, 5.5)
- `DiffStats` component: shows chunk count, avg char size, avg boundary quality side by side; highlights winner per metric in green (Phase 5.3)
- Compare toggle in App header — switches single ↔ compare mode; persisted in `localStorage` (Phase 5.4)
- `ExportButton` rewritten: "Export Config" downloads JSON with `strategy`, `chunk_size`, `chunk_overlap`, `strategy_params`, `regex_patterns`; "Export Results ▾" dropdown offers JSON / JSONL / YAML formats (Phase 6.4)
- JSONL export: one chunk per line with `index`, `text`, `metadata`, `token_count` — ready for vector DB ingestion (Phase 6.1)
- YAML export via `js-yaml` on frontend; no backend changes required (Phase 6.2)
- All exports trigger file download via `Blob` + `URL.createObjectURL`; filename pattern `chunklab_export_{ISO-timestamp}.{ext}` (Phase 6.3)
- `md_metadata.py`: `extract_header_path()` scans full markdown with regex, builds `"H1 > H2 > H3"` stack for any chunk's position; `md_path_metadata()` wraps it as a `_md_path` metadata dict (Phase 7.1–7.2)
- `/api/chunk` now prepends `_md_path` metadata to each chunk's metadata list when the chunk has preceding headers (Phase 7.3)
- `ChunkCard` renders `_md_path` as a breadcrumb trail (`Section › Subsection › Topic`) above chunk text; `_md_path` is hidden from the user metadata badges (Phase 7.4)
- `test_md_metadata.py`: 11 tests for header path extraction and metadata dict generation (Phase 7)

### Changed
- `ExportButton` replaced clipboard-only "Export JSON" with file-download-based multi-format export (Phase 6.3)

### Changed
- CHANGELOG reformatted to English per Keep a Changelog spec (Phase 0.1)
- README Architecture section updated: fixed-size is the only implemented strategy; recursive/semantic/token-aware listed as roadmap (Phase 0.2)
- README Feature List: added accurate "Chunking Strategy" entry, moved unimplemented strategies to roadmap item (Phase 0.2)

### Security
- CORS origins now read from `FRONTEND_ORIGIN` env var; defaults to `localhost:5173` and `127.0.0.1:5173`; `ELECTRON_MODE=true` retains wildcard for packaged desktop app (Phase 0.3)

---

## [1.0.0] - 2026-04-18

### Added
- **GitHub Actions (CI/CD)**:
  - `test.yml`: Pengujian otomatis Python dengan `pytest` dan `coverage`.
  - `lint.yml`: Pengecekan kode dengan `ruff`, `black`, `mypy` (Python) dan `tsc` (TypeScript).
  - `security.yml`: Pemindaian keamanan dengan `bandit`, `pip-audit`, dan `npm audit`.
  - `dco.yml`: Verifikasi Developer Certificate of Origin (DCO) untuk kontribusi PR.
- **Branding**:
  - Logo resmi aplikasi (`logo.png`) dan screenshot antarmuka (`screenshot.png`).
  - Integrasi logo pada Header aplikasi dan About Modal.
  - Badge status workflow pada `README.md`.
- **Infrastruktur OSS**:
  - Lisensi Apache-2.0, file NOTICE, dan CODE_OF_CONDUCT.md.
  - Template Issue dan Pull Request di GitHub.
- **Frontend**:
  - `RegexReference.jsx`: Panel referensi interaktif untuk panduan regex (Karakter umum, Kuantifier, Anchor, dll).
  - Pengecekan tipe statis dengan TypeScript (`tsconfig.json`).
  - Fallback untuk `crypto.randomUUID()` di konteks non-secure (seperti HTTP biasa).
- **Backend**:
  - Skrip `add_license_headers.py` untuk otomatisasi penambahan header lisensi.

### Changed
- **Backend Optimization**:
  - Peningkatan performa pada ekstraksi metadata regex.
  - Refaktor proses tokenisasi agar berjalan secara paralel.
- **Frontend Refactor**:
  - Migrasi logika utama ke dalam custom hooks (`useChunker`, `useRegexPatterns`, `useTokenization`) untuk kode yang lebih modular.
- **Dependencies**:
  - Update FastAPI ke v0.136.0 untuk menambal kerentanan keamanan pada Starlette.
  - Update dependensi pengujian ke `pytest` v9.0.3 dan `pytest-asyncio` v1.3.0.
- **Project Structure**:
  - Peningkatan `.gitignore` untuk menyaring artefak build Electron, PyInstaller, dan cache linter.

### Fixed
- Perbaikan error linting PEP8 (E402) dan penghapusan variabel/import yang tidak digunakan.
- Sinkronisasi `package-lock.json` untuk memastikan build CI/CD yang konsisten.
- Penyesuaian `security.yml` untuk memfilter temuan keamanan tingkat rendah agar tidak memblokir workflow utama.

---

*Terima kasih kepada semua kontributor dan AI Coding Agents yang membantu mempercepat pengembangan proyek ini.*
