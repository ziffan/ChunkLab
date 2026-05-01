<div align="center">
  <img src="frontend/public/logo.png" alt="ChunkLab Banner" width="500">
  
  # ChunkLab

  [![Test](https://github.com/ziffan/ChunkLab/actions/workflows/test.yml/badge.svg)](https://github.com/ziffan/ChunkLab/actions/workflows/test.yml)
  [![Lint](https://github.com/ziffan/ChunkLab/actions/workflows/lint.yml/badge.svg)](https://github.com/ziffan/ChunkLab/actions/workflows/lint.yml)
  [![Security Scan](https://github.com/ziffan/ChunkLab/actions/workflows/security.yml/badge.svg)](https://github.com/ziffan/ChunkLab/actions/workflows/security.yml)
  [![DCO](https://img.shields.io/badge/DCO-required-orange)](https://github.com/ziffan/ChunkLab/actions/workflows/dco.yml)
  [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
  [![React](https://img.shields.io/badge/react-18-61dafb)](https://reactjs.org/)

  **The interactive sandbox for text chunking experimentation — built for RAG pipelines.**
</div>

---

### Pitch

**EN:** ChunkLab is a browser-based sandbox for testing, visualizing, and validating text chunking strategies before deploying them into a RAG (Retrieval-Augmented Generation) pipeline. It supports five chunking strategies, per-chunk quality metrics, semantic retrieval simulation, side-by-side comparison mode, and multi-format export.

**ID:** ChunkLab adalah sandbox berbasis browser untuk menguji, memvisualisasikan, dan memvalidasi strategi chunking teks sebelum diterapkan ke pipeline RAG. Mendukung lima strategi chunking, quality metrics per chunk, simulasi retrieval semantik, mode perbandingan dua konfigurasi, dan export multi-format.

---

### Screenshot

<div align="center">
  <img src="frontend/public/screenshot.png" alt="ChunkLab Dashboard" width="800">
</div>

---

### Quickstart

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

---

### Fitur

| Fitur | Status |
|---|---|
| **5 strategi chunking** — Fixed, Recursive, Token-aware (tiktoken), Sentence (pysbd), Markdown Structure | ✅ |
| **File upload** — drag-and-drop / klik untuk `.txt` / `.md` hingga 500 KB | ✅ |
| **Quality metrics** per chunk — Boundary Quality, Information Density, completeness flag | ✅ |
| **Markdown breadcrumb** — jalur header H1 › H2 › H3 otomatis per chunk | ✅ |
| **Regex metadata** — ekstraksi otomatis dengan capture group | ✅ |
| **Retrieval simulation** — query semantik top-K via `all-MiniLM-L6-v2` (opsional) | ✅ |
| **Comparison mode** — dua konfigurasi side-by-side dengan diff stats | ✅ |
| **Export multi-format** — JSON, JSONL (siap Vector DB), YAML sebagai file download | ✅ |
| **Config export** — simpan konfigurasi strategy + params + regex ke JSON | ✅ |
| **API Spec download** — unduh OpenAPI spec langsung dari UI | ✅ |
| **Token estimation** — multi-provider: OpenAI, Gemini, Anthropic, Ollama, LM Studio, OpenRouter | ✅ |
| **Overlap visualization** — highlight amber/cyan untuk area overlap antar chunk | ✅ |
| **MOCK\_MODE** — banner peringatan ketika berjalan tanpa tokenizer nyata | ✅ |
| Docker Compose one-command startup | 🔜 |
| Updated screenshots | 🔜 |

---

### Arsitektur

```
POST /api/chunk
  └─ ChunkRequest (strategy, strategy_params, regex_patterns)
       ├─ chunk_by_strategy() → FixedSizeChunker / RecursiveCharacterChunker /
       │                         TokenAwareChunker / SentenceChunker / MarkdownStructureChunker
       ├─ extract_metadata_from_compiled()   ← regex patterns
       ├─ md_path_metadata()                 ← header breadcrumb
       └─ boundary_quality / information_density / is_complete

POST /api/retrieve
  └─ RetrieveRequest (query, chunks, top_k)
       └─ retriever.retrieve() → cosine similarity via sentence-transformers (opsional)

POST /api/tokenize   ← tiktoken / Ollama / mock
GET  /api/health     ← mock_mode flag
GET  /openapi.json   ← OpenAPI spec (FastAPI built-in)
```

**Backend:** FastAPI + Pydantic v2, Python 3.12  
**Frontend:** React 18 + Tailwind CSS + Vite, hooks-based architecture  
**Tes:** 98 tests (pytest), type-check bersih (tsc --noEmit)

---

### Pengembangan

```bash
# Jalankan semua test
pytest backend/tests/ -v

# Test dengan coverage
pytest backend/tests/ -v --cov=backend/services --cov=backend/routers

# Linting
ruff check backend/
black --check backend/
mypy backend/ --ignore-missing-imports

# TypeScript check
cd frontend && npm run type-check
```

Lihat [CHANGELOG](CHANGELOG.md) untuk riwayat perubahan lengkap per phase.

---

### Lisensi

Proyek ini dilisensikan di bawah **Apache License 2.0**. Lihat file [LICENSE](LICENSE) untuk detail.

Copyright © 2026 Ziffan (Ziffany Firdinal).
