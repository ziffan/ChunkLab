# Changelog

Semua perubahan signifikan pada proyek **ChunkLab** akan didokumentasikan di file ini.

Format ini didasarkan pada [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), dan proyek ini mematuhi [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
