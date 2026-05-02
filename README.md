<div align="center">
  <img src="frontend/public/logo.png" alt="ChunkLab Banner" width="500">
  
  # ChunkLab

  [![Test](https://github.com/ziffan/ChunkLab/actions/workflows/test.yml/badge.svg)](https://github.com/ziffan/ChunkLab/actions/workflows/test.yml)
  [![Lint](https://github.com/ziffan/ChunkLab/actions/workflows/lint.yml/badge.svg)](https://github.com/ziffan/ChunkLab/actions/workflows/lint.yml)
  [![Docker Build](https://github.com/ziffan/ChunkLab/actions/workflows/docker.yml/badge.svg)](https://github.com/ziffan/ChunkLab/actions/workflows/docker.yml)
  [![Security Scan](https://github.com/ziffan/ChunkLab/actions/workflows/security.yml/badge.svg)](https://github.com/ziffan/ChunkLab/actions/workflows/security.yml)
  [![DCO](https://img.shields.io/badge/DCO-required-orange)](https://github.com/ziffan/ChunkLab/actions/workflows/dco.yml)
  [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
  [![React](https://img.shields.io/badge/react-18-61dafb)](https://reactjs.org/)

  **The interactive sandbox for text chunking experimentation — built for RAG pipelines.**
</div>

---

### Pitch

**EN:** ChunkLab is a browser-based sandbox for testing, visualizing, and validating text chunking strategies before deploying them into a RAG (Retrieval-Augmented Generation) pipeline. It supports seven chunking strategies (including two purpose-built for Indonesian text), per-chunk quality metrics, semantic retrieval simulation, side-by-side comparison mode, and multi-format export.

**ID:** ChunkLab adalah sandbox berbasis browser untuk menguji, memvisualisasikan, dan memvalidasi strategi chunking teks sebelum diterapkan ke pipeline RAG. Mendukung tujuh strategi chunking (termasuk dua khusus teks Indonesia), quality metrics per chunk, simulasi retrieval semantik, mode perbandingan dua konfigurasi, dan export multi-format.

---

### Screenshot

<div align="center">
  <img src="frontend/public/screenshot.png" alt="ChunkLab Dashboard" width="800">
</div>

---

### Quickstart

#### Docker (cara tercepat)

**Prerequisites:** Docker Desktop

```bash
git clone https://github.com/ziffan/ChunkLab.git
cd ChunkLab
cp backend/.env.example backend/.env   # sesuaikan API key jika perlu
docker compose up --build
# UI tersedia di http://localhost:80
```

> **Ollama / LM Studio:** Jika Anda menjalankan Ollama atau LM Studio di host, keduanya sudah dikonfigurasi otomatis via `host.docker.internal` — tidak perlu ubah apapun.

---

#### Manual (untuk development)

**Prerequisites:** Python 3.12+, Node.js 18+

#### 1. Backend

```bash
git clone https://github.com/ziffan/ChunkLab.git
cd ChunkLab

python -m venv backend/.venv

# Windows
backend\.venv\Scripts\activate
# Linux/macOS
source backend/.venv/bin/activate

pip install -r backend/requirements.txt
cp backend/.env.example backend/.env   # lalu sesuaikan jika perlu

python -m backend.main
# Backend tersedia di http://127.0.0.1:8000
```

#### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# UI tersedia di http://localhost:5173
```

#### 3. Retrieval (opsional)

Untuk mengaktifkan fitur Retrieval Simulation, install dependensi tambahan:

```bash
pip install -r requirements-retrieval.txt
```

Model yang digunakan: `intfloat/multilingual-e5-large` (mendukung Bahasa Indonesia dan 100+ bahasa lain).

> **Catatan:** Model `intfloat/multilingual-e5-large` (~560 MB) diunduh otomatis saat pertama kali dipakai dan di-cache di `~/.cache/huggingface/` (atau volume `hf_cache` di Docker).

---

### Kebutuhan Sistem

| Komponen | Minimum | Rekomendasi |
|---|---|---|
| **Python** | 3.12 | 3.12+ |
| **Node.js** | 18 | 20 LTS |
| **RAM (mode dasar)** | 512 MB | 1 GB |
| **RAM (dengan Retrieval)** | 4 GB | 8 GB |
| **Disk (model embedding)** | — | ~1 GB (multilingual-e5-large, diunduh otomatis) |
| **GPU** | Tidak wajib | CUDA GPU mempercepat encoding retrieval |
| **OS** | Windows 10 / Ubuntu 20.04 / macOS 12 | Windows 11 / Ubuntu 22.04 / macOS 14 |

> **Catatan:** Fitur Retrieval Simulation membutuhkan RAM ekstra karena model embedding `intfloat/multilingual-e5-large` (~560 MB) di-load ke memori. Tanpa fitur ini, aplikasi berjalan ringan di mesin apa pun yang memenuhi syarat Python 3.12 dan Node.js 18.
>
> **CUDA di Docker:** Secara default encoding berjalan di CPU dan sudah cukup untuk penggunaan normal. Untuk mengaktifkan CUDA di Docker, dibutuhkan NVIDIA Container Toolkit di host, base image berbasis `nvidia/cuda`, dan konfigurasi `deploy.resources.reservations.devices` di `docker-compose.yml` — tidak disertakan di konfigurasi default.

---

### Fitur

| Fitur | Status |
|---|---|
| **6 strategi chunking** — Fixed, Recursive, Token-aware, Sentence (`sentence_id`, +pysbd), Legal Indonesia (`legal_id`), Markdown Structure | ✅ |
| **File upload** — drag-and-drop / klik untuk `.txt` / `.md` hingga 500 KB | ✅ |
| **Quality metrics** per chunk — Boundary Quality, Information Density, completeness flag | ✅ |
| **Markdown breadcrumb** — jalur header H1 › H2 › H3 otomatis per chunk | ✅ |
| **Regex metadata** — ekstraksi otomatis dengan capture group | ✅ |
| **Retrieval simulation** — query semantik top-K (5/10/25/50) via `multilingual-e5-large` (opsional) | ✅ Diuji (Docker) |
| **Comparison mode** — dua konfigurasi side-by-side dengan diff stats | ✅ |
| **Export multi-format** — JSON, JSONL (siap Vector DB), YAML sebagai file download | ✅ |
| **Token estimation** — multi-provider: OpenAI, Gemini, Ollama, LM Studio, OpenRouter | ✅ |
| **Overlap visualization** — highlight amber/cyan untuk area overlap antar chunk | ✅ |
| **Docker Compose** — `docker compose up --build` starts backend + frontend | ✅ |

---

### Dokumentasi

| Dokumen | Isi |
|---|---|
| [docs/getting-started.md](docs/getting-started.md) | Setup manual (backend, frontend, retrieval, env) |
| [docs/strategies.md](docs/strategies.md) | Panduan pemilihan strategi, legal_id metadata, token estimation |
| [docs/architecture.md](docs/architecture.md) | Request flow (Mermaid), component overview, versioning policy |
| [CHANGELOG.md](CHANGELOG.md) | Riwayat perubahan |

---

### Arsitektur (ringkas)

**Backend:** FastAPI + Pydantic v2, Python 3.12  
**Frontend:** React 18 + Tailwind CSS + Vite, hooks-based architecture  
**Tests:** 137 tests (pytest), type-check bersih (tsc --noEmit)  
**Versi:** v0.2.0

Lihat [docs/architecture.md](docs/architecture.md) untuk diagram request flow lengkap.

---

### Pengembangan

```bash
# Jalankan semua test
pytest backend/tests/ -v

# Linting
ruff check backend/
black --check backend/
mypy backend/ --ignore-missing-imports --explicit-package-bases

# TypeScript check
cd frontend && npm run type-check
```

Lihat [CHANGELOG](CHANGELOG.md) untuk riwayat perubahan lengkap.

---

### Lisensi

Proyek ini dilisensikan di bawah **Apache License 2.0**. Lihat file [LICENSE](LICENSE) untuk detail.

Copyright © 2026 Ziffan (Ziffany Firdinal).
