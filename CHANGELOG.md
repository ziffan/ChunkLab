# Changelog

All notable changes to ChunkLab will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2026-08-17

### Security
- `axios` bumped `1.16.0 → 1.19.0` — fixes high-severity CVEs beyond the 0.2.2 patch (DoS via recursion, prototype pollution, proxy bypass)
- `js-yaml` bumped `4.3.0 → 4.3.1` — fixes CVE-2026-59870 (quadratic CPU DoS via `!!omap` resolution)
- Regenerated orphaned root `package-lock.json` — it had been locking the full electron-builder toolchain (electron, node-tar, brace-expansion, extract-zip, etc.) at unpatched versions since before Electron was removed in 0.2.0, despite root `package.json` declaring zero dependencies; cleared 45 Dependabot alerts

### Fixed
- CI Lint workflow (`lint.yml`) had been failing on master since the 0.2.2 mistune bump: `ruff`/`black`/`mypy` were installed unpinned and CI had silently picked up a newer ruff release with a broader default rule set. Fixed the 37 findings (import sorting, `typing.X` → builtin generics, 6 justified `noqa: BLE001` on external-service-probe boundaries) and pinned tool versions in CI

---

## [0.2.2] - 2026-07-26

### Security
- `mistune` bumped `3.2.1 → 3.3.4` — fixes 19 CVEs (CVE-2026-59922 through CVE-2026-59930, plus CVE-2026-44708, CVE-2026-44896, and 7 additional DoS/XSS vulnerabilities)

---

## [0.2.1] - 2026-06-29

### Security
- `form-data` patched: CRLF injection via unescaped multipart field/filenames ([GHSA-hmw2-7cc7-3qxx](https://github.com/advisories/GHSA-hmw2-7cc7-3qxx))
- `js-yaml` patched: quadratic-complexity DoS via repeated merge-key aliases ([GHSA-h67p-54hq-rp68](https://github.com/advisories/GHSA-h67p-54hq-rp68))
- `esbuild` patched: dev server accepts cross-origin requests ([GHSA-67mh-4wv8-2f99](https://github.com/advisories/GHSA-67mh-4wv8-2f99)) — resolved by upgrading `vite` 5 → 8 and `@vitejs/plugin-react` 4 → 6

---

## [0.2.0] - 2026-05-02

### Added
- `ChunkLegend` component above the chunk grid — explains all per-chunk indicators: BQ dot colors (🟢/🟡/🔴), Information Density, ⚠ trun, overlap highlight colors (amber = inherited from previous chunk, cyan = passed to next), and token badge color coding (green/yellow/orange/red/blue + MOCK/MIN/MAX labels)
- Retrieval panel: Top-K selector with options 5 / 10 / 25 / 50 (previously hardcoded to 5); backend already supported up to 50
- `sentence_id` strategy now supports 23 pysbd languages in addition to Indonesian (pysbd optional; falls back to regex splitter when not installed or language is unsupported)
- `RETRIEVAL_MODEL` env var: override the embedding model used for Retrieval Simulation (default `intfloat/multilingual-e5-large`)
- Docker Compose support: `docker compose up --build` starts backend + frontend; named volume `hf_cache` persists the retrieval model across restarts

### Fixed
- `frontend/nginx.conf`: proxy timeout raised from 60 s to 300 s — prevents 504 Gateway Timeout during retrieval model warm-up
- `backend/Dockerfile`: `requirements-retrieval.txt` now installed by default so Retrieval Simulation works out of the box
- Ollama and LM Studio unreachable from Docker container — `docker-compose.yml` overrides base URLs to `http://host.docker.internal:{port}` and adds `extra_hosts: host-gateway` for Linux
- mypy CI: resolved 8 type errors; now fully enforced (removed `|| true`)
- bandit CI: exclude `backend/.venv`; removed `--exit-zero` to enforce zero high-severity findings in application code

### Changed
- Electron desktop app support removed — app is now web-only; Docker Compose is the recommended deployment path
- `sentence` strategy removed; all functionality merged into `sentence_id` (use `language` param to select pysbd-supported languages)
- BQ legend moved from Regex Patterns panel to dedicated `ChunkLegend` component

---

## [0.1.0] - 2026-04-30

Initial feature-complete release.

### Chunking strategies
- `fixed` — character-based fixed-size with overlap
- `recursive` — splits by `\n\n` → `\n` → `. ` → ` ` → char; respects paragraph boundaries
- `token` — tiktoken-based exact token count chunking (`cl100k_base`, `p50k_base`, `o200k_base`)
- `sentence_id` — Indonesian sentence chunker (regex + abbreviation list); params `max_sentences_per_chunk`, `overlap_sentences`, `min_chunk_chars`
- `markdown` — splits at header boundaries (mistune AST); oversized sections sub-split by character
- `legal_id` — splits Indonesian regulatory documents (UU/PP/Perpres/Perda) at Pasal/BAB boundaries; auto-injects `_legal_path`, `_legal_section`, `_legal_unit`, `_legal_number` metadata per chunk

### Quality metrics
- `boundary_quality` (0–1), `information_density`, `is_complete` (mid-word cut detection) per chunk
- `QualityBadge` component: colored dot + BQ%/ID% display + ⚠ trun warning

### Retrieval Simulation
- `POST /api/retrieve` via `intfloat/multilingual-e5-large`; cosine similarity top-K ranking
- Optional install (`requirements-retrieval.txt`); graceful 503 degradation when not available

### Export
- JSON, JSONL (vector DB ready), YAML — file download
- Config export: `strategy`, `chunk_size`, `chunk_overlap`, `strategy_params`, `regex_patterns`
- OpenAPI spec download from UI

### Other features
- File upload: drag-and-drop `.txt`/`.md` up to 500 KB
- Regex metadata extraction with capture group support; in-app Regex Reference panel
- Markdown breadcrumb (`_md_path`) per chunk
- Comparison mode: two configs side-by-side with diff stats
- Token estimation: OpenAI, Ollama (native + tiktoken proxy fallback), LM Studio, OpenRouter, Gemini, Mock
- `MOCK_MODE` banner when running without a real tokenizer
- CI/CD: pytest, ruff, black, mypy, tsc, bandit, pip-audit, npm audit, DCO check

---

*Thanks to all contributors and AI coding agents who helped build this project.*
