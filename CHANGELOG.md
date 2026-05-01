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
