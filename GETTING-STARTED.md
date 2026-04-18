# Cara Memulai ChunkLab

Panduan langkah demi langkah untuk menjalankan aplikasi ini dari nol.

---

## Prasyarat

Pastikan software berikut sudah terinstall di komputer Anda:

| Software | Versi Minimum | Cek Versi | Link Download |
|---|---|---|---|
| Python | 3.10+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| npm | (ikut Node.js) | `npm --version` | — |

> **Windows:** Saat install Python, centang opsi **"Add Python to PATH"**.

---

## Langkah 1 — Clone / Download Project

Jika belum ada folder project-nya, clone atau download dan buka terminal di folder `ChunkingSanbox`:

```bash
cd D:\PROYEK\ChunkingSanbox
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

### 2.3 Buat File Konfigurasi `.env`

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
| `MOCK_MODE` | `true` | Gunakan mock tokenizer (tanpa API key) |
| `OPENAI_API_KEY` | `your-key-here` | API key OpenAI (opsional) |
| `GEMINI_API_KEY` | `your-key-here` | API key Gemini (opsional) |
| `ANTHROPIC_API_KEY` | `your-key-here` | API key Anthropic (opsional) |
| `OPENROUTER_API_KEY` | `your-key-here` | API key OpenRouter (opsional) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL Ollama (jika dipakai) |
| `LM_STUDIO_BASE_URL` | `http://localhost:1234` | URL LM Studio (jika dipakai) |

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

1. Paste teks Markdown ke editor (kolom kiri)
2. Atur **Chunk Size** dan **Overlap** dengan slider
3. Tambahkan **Regex Pattern** untuk menangkap metadata (misal: `Pasal\s+(\d+)`)
4. Klik **Estimate Tokens** untuk menghitung token per chunk
5. Klik **Export JSON** untuk menyalin hasil ke clipboard

---

## Langkah 6 — Verifikasi

### Cek Backend Health

```bash
# Windows PowerShell
Invoke-RestMethod http://localhost:8000/api/health

# Linux / macOS / Git Bash
curl http://localhost:8000/api/health
```

Harus mengembalikan: `{"status":"ok","version":"1.0.0"}`

### Jalankan Test Backend

```bash
python -m pytest backend/tests/ -q
```

Semua test harus **PASSED**.

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
| `ModuleNotFoundError: No module named 'backend'` | Pastikan menjalankan perintah dari **root folder** project (`ChunkingSanbox/`), bukan dari dalam folder `backend/` |
| `pip` tidak dikenali | Install Python dengan opsi pip, atau coba `python -m pip install ...` |
| `npm install` gagal / lambat | Coba hapus `node_modules` dan `package-lock.json`, lalu jalankan lagi `npm install` |
| CORS error di browser | Pastikan `FRONTEND_ORIGIN` di `backend/.env` sama dengan URL frontend (`http://localhost:5173`) |
| Port 8000 sudah dipakai | Ubah `BACKEND_PORT` di `.env` ke port lain (misal `8001`) |
| Port 5173 sudah dipakai | Jalankan `npm run dev -- --port 5174` dan sesuaikan `FRONTEND_ORIGIN` di `.env` |
| Tokenizer error / API key invalid | Set `MOCK_MODE=true` di `.env` untuk gunakan estimator lokal tanpa API key |
| venv tidak bisa diaktifkan di PowerShell | Jalankan `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` lalu coba lagi |
