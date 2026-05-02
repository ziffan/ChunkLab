# Cara Memulai ChunkLab

Panduan langkah demi langkah untuk menjalankan aplikasi ini dari nol.

---

## Opsi A — Docker (cara tercepat)

Jika Anda hanya ingin mencoba ChunkLab tanpa setup Python/Node.js, gunakan Docker:

**Prasyarat:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/ziffan/ChunkLab.git
cd ChunkLab

# Buat file konfigurasi (opsional — default sudah bisa langsung jalan)
cp backend/.env.example backend/.env

# Jalankan semua service
docker compose up --build
```

Buka browser ke **http://localhost:80**.

> **Ollama / LM Studio di host:** Token estimation via Ollama atau LM Studio otomatis bekerja tanpa konfigurasi tambahan — `docker-compose.yml` sudah mengarahkan koneksi ke host machine via `host.docker.internal`.

> **Retrieval Simulation:** Sudah termasuk di Docker image secara default. Model embedding (`intfloat/multilingual-e5-large`, ~560 MB) diunduh otomatis saat pertama kali dipakai dan di-cache di volume `hf_cache`.

---

## Opsi B — Setup Manual (untuk development)

---

## Prasyarat

Pastikan software berikut sudah terinstall di komputer Anda:

| Software | Versi Minimum | Cek Versi | Link Download |
|---|---|---|---|
| Python | 3.12+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| npm | (ikut Node.js) | `npm --version` | — |

> **Windows:** Saat install Python, centang opsi **"Add Python to PATH"**.

---

## Langkah 1 — Clone / Download Project

```bash
git clone https://github.com/ziffan/ChunkLab.git
cd ChunkLab
```

---

## Langkah 2 — Setup Backend

### 2.1 Buat Virtual Environment (disarankan)

Virtual environment mengisolasi dependency agar tidak bentrok dengan project Python lain.

```bash
# Windows
python -m venv backend\.venv
backend\.venv\Scripts\activate

# Linux / macOS
python3 -m venv backend/.venv
source backend/.venv/bin/activate
```

> Setelah activate, prompt terminal akan berubah menjadi `(.venv)` di awal baris.

### 2.2 Install Dependency Backend

```bash
pip install -r backend/requirements.txt
```

### 2.3 Install Dependency Retrieval (Opsional)

Untuk mengaktifkan fitur **Retrieval Simulation** (pencarian semantik top-K), install dependensi tambahan:

```bash
pip install -r requirements-retrieval.txt
```

Model yang digunakan: `intfloat/multilingual-e5-large` (~560 MB, diunduh otomatis saat pertama kali dipakai). Butuh minimal **4 GB RAM** tersedia. Lewati langkah ini jika tidak membutuhkan fitur retrieval.

> **Catatan:** Model embedding diunduh otomatis (~560 MB) pada penggunaan pertama.

### 2.4 Buat File Konfigurasi `.env`

```bash
# Windows (PowerShell)
Copy-Item backend\.env.example backend\.env

# Linux / macOS
cp backend/.env.example backend/.env
```

File `.env` sudah berisi konfigurasi default yang langsung bisa dipakai. Untuk mulai cepat tanpa API key, biarkan `MOCK_MODE=true`.

<details>
<summary>📋 Daftar Variabel `.env`</summary>

| Variable | Default | Keterangan |
|---|---|---|
| `BACKEND_PORT` | `8000` | Port backend |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Origin frontend (CORS) |
| `ELECTRON_MODE` | `false` | Set `true` saat berjalan sebagai Electron desktop app |
| `MOCK_MODE` | `true` | Gunakan mock tokenizer (tanpa API key) |
| `OPENAI_API_KEY` | `your-key-here` | API key OpenAI (opsional) |
| `GEMINI_API_KEY` | `your-key-here` | API key Google Gemini (opsional) |
| `OPENROUTER_API_KEY` | `your-key-here` | API key OpenRouter (opsional) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL Ollama lokal (opsional) |
| `LM_STUDIO_BASE_URL` | `http://localhost:1234` | URL LM Studio lokal (opsional) |

</details>

---

## Langkah 3 — Setup Frontend

Buka **terminal baru** (biarkan terminal backend tetap berjalan):

```bash
cd frontend
npm install
```

> Proses ini hanya perlu sekali. `npm install` akan mengunduh semua dependency frontend.

---

## Langkah 4 — Jalankan Aplikasi

Anda perlu **dua terminal** yang berjalan bersamaan.

### Terminal 1 — Backend

```bash
# Pastikan venv aktif (lihat langkah 2.1)
python -m backend.main
```

Jika berhasil, akan muncul:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Jika berhasil, akan muncul:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

---

## Langkah 5 — Buka di Browser

Buka browser ke **http://localhost:5173**

Anda akan melihat tampilan dua kolom: editor di kiri, output chunk di kanan.

### Coba Segera

1. Paste teks Markdown atau upload file `.txt` / `.md` ke editor (kolom kiri)
2. Pilih **Strategy** — mulai dengan *Fixed Size* untuk eksplorasi awal
3. Atur **Chunk Size** dan **Overlap** dengan slider (khusus strategi Fixed/Recursive)
4. Tambahkan **Regex Pattern** untuk menangkap metadata (misal: `Pasal\s+(\d+)`)
5. Klik **Estimate Tokens** untuk menghitung token per chunk — provider yang didukung: Mock, OpenAI, Google Gemini, OpenRouter, Ollama, LM Studio
6. Aktifkan **Compare Mode** di header untuk membandingkan dua konfigurasi secara berdampingan
7. Klik **Export Results** dan pilih format JSON / JSONL / YAML untuk mengunduh hasil

**Tip strategi Bahasa Indonesia:** Gunakan `Sentence — Indonesian (sentence_id)` untuk teks narasi/berita, atau `Legal Structure — Indonesian (legal_id)` untuk dokumen UU/PP/Perpres.

---

## Langkah 6 — Verifikasi

### Cek Backend Health

```bash
# Windows PowerShell
Invoke-RestMethod http://localhost:8000/api/health

# Linux / macOS / Git Bash
curl http://localhost:8000/api/health
```

Harus mengembalikan JSON dengan `"status": "ok"` dan field `"mock_mode"` (true/false sesuai konfigurasi `.env`).

### Jalankan Test Backend

```bash
python -m pytest backend/tests/ -q
```

Harus menampilkan **138 passed**.

### Build Frontend (Production)

```bash
cd frontend
npm run build
```

Output ada di `frontend/dist/`.

---

## Troubleshooting

| Masalah | Solusi |
|---|---|
| `python` tidak dikenali | Install Python dan centang "Add to PATH", atau gunakan `python3` / `py` |
| `ModuleNotFoundError: No module named 'backend'` | Pastikan menjalankan perintah dari **root folder** project (`ChunkLab/`), bukan dari dalam folder `backend/` |
| `pip` tidak dikenali | Install Python dengan opsi pip, atau coba `python -m pip install ...` |
| `npm install` gagal / lambat | Coba hapus `node_modules` dan `package-lock.json`, lalu jalankan lagi `npm install` |
| CORS error di browser | Pastikan `FRONTEND_ORIGIN` di `backend/.env` sama dengan URL frontend (`http://localhost:5173`) |
| Port 8000 sudah dipakai | Ubah `BACKEND_PORT` di `.env` ke port lain (misal `8001`) |
| Port 5173 sudah dipakai | Jalankan `npm run dev -- --port 5174` dan sesuaikan `FRONTEND_ORIGIN` di `.env` |
| Tokenizer error / API key invalid | Set `MOCK_MODE=true` di `.env` untuk gunakan estimator lokal tanpa API key |
| Estimasi token Ollama tidak akurat | Pastikan Anda menggunakan model LLM generatif (contoh `qwen3.5:4b`), bukan model embedding (`bge-m3`, `nomic-embed-text`) — model embedding tidak punya endpoint tokenisasi yang kompatibel |
| Retrieval tidak muncul di UI | Install `requirements-retrieval.txt` lalu restart backend |
| venv tidak bisa diaktifkan di PowerShell | Jalankan `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` lalu coba lagi |
