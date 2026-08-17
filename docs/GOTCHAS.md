# Gotchas

Jebakan yang sudah ditemukan di project ini. Baca sebelum menyentuh area terkait —
jangan mengulang riset yang sudah dibayar mahal.

## Windows / PowerShell / Bash tooling

### 1. Heredoc `>` di PowerShell 5.1 merusak commit message
PowerShell 5.1 memperlakukan `>` sebagai redirection operator **di dalam heredoc commit
message**, bahkan ketika `>` ada di dalam quoted string yang dikirim ke native
executable seperti `git`.

**Symptom:** `git commit` exit dengan `error: pathspec '>' did not match any file(s)` —
commit tidak benar-benar terbuat.

**Fix:** Hindari `>`/`<` sama sekali di commit message yang ditulis via PowerShell
heredoc (`@'...'@` atau `@"..."@`). Contoh: "add H1 > H2 header path metadata" →
"add H1-to-H2 header path metadata".

### 2. `&&` tidak ada di PowerShell 5.1
Pipeline chain operator `&&` cuma ada di PowerShell 7+, bukan Windows PowerShell 5.1.

**Fix:** Chain command dengan `; if ($?) { ... }`, atau pecah jadi panggilan Bash tool
terpisah.

### 3. Selalu pakai absolute path untuk linting tools di PowerShell
`ruff`, `black`, `mypy`, `pytest` dari PowerShell bisa silent-fail atau target folder
yang salah kalau dikasih relative path (`backend/`), tergantung state working
directory.

```powershell
# Benar
ruff check "D:\PROYEK\ChunkingSanbox\backend"
black --check "D:\PROYEK\ChunkingSanbox\backend"
pytest "D:\PROYEK\ChunkingSanbox\backend\tests" -v

# Hindari
ruff check backend/
```

### 4. Pakai Bash tool (bukan PowerShell) untuk multi-step shell chain
Untuk sequence seperti `cd frontend && npm run type-check`, pakai Bash tool dengan
sintaks POSIX — menghindari jebakan operator PowerShell di atas.

### 5. Node.js v24+ butuh `--use-system-ca` di belakang proxy korporat
Node.js v24 tidak lagi pakai Windows system certificate store secara default. Di
mesin dengan SSL inspection/corporate CA, semua `npm install`/`npm audit` gagal dengan
`UNABLE_TO_VERIFY_LEAF_SIGNATURE`.

**Fix (sudah diterapkan):** `NODE_OPTIONS=--use-system-ca` di-set permanen sebagai
Windows user environment variable. Untuk PowerShell tool: `$env:NODE_OPTIONS =
"--use-system-ca"; npm install ...`. Untuk Bash tool: prefix
`NODE_OPTIONS=--use-system-ca npm install ...`. `npm audit fix` juga kena — fix yang
sama berlaku.

### 6. Bash tool `cd` persist antar panggilan — merusak deteksi import-sort ruff
Working directory Bash tool persist antar panggilan tool. Command `cd frontend && ...`
meninggalkan panggilan berikutnya tetap berjalan dari `frontend/`, bahkan yang pakai
absolute path.

**Symptom:** `ruff check "D:\...\backend"` (absolute path) memberi hasil `I001`
(import-block-unsorted) **berbeda** tergantung cwd shell saat itu repo root atau
`frontend/` — repo ini tidak punya `pyproject.toml`/`ruff.toml`, jadi deteksi
known-first-party ruff untuk import `backend.*` jatuh ke heuristik berbasis cwd, bukan
cuma target path. Lihat docs/DECISIONS.md (Pending) untuk rencana fix permanen via
config file.

**Fix:** Selalu `cd` balik ke repo root (atau buka panggilan Bash baru) sebelum
`ruff check` setelah command apapun yang pindah direktori. Jangan percaya absolute
target path saja membuat hasil cwd-independent.

## Python / backend

### 7. mypy narrowing untuk return type mistune 3.3.x
`backend/services/chunkers/markdown_struct.py:45` — mistune 3.3.4 mengekspos return
type eksplisit `str | list[...]` untuk `md(text)`.

**Fix:** Ganti `if not ast_nodes` dengan
`if not isinstance(ast_nodes, list) or not ast_nodes` — ini menyempitkan (narrow) tipe
dan memuaskan mypy. Berlaku sejak mistune 3.2.1, masih valid di 3.3.x.

### 8. legal_id — artefak PDF Indonesian legal documents
Dokumen legal Indonesia hasil konversi PDF sering punya struktur baris rusak. Tiga
masalah yang sudah ditemukan dan fix-nya, di `backend/services/chunkers/legal_id.py`:

1. **Inline Pasal headers** — PDF converter menggabung `Pasal N` dan konten jadi satu
   baris. Fix: `_RE_PASAL = re.compile(r"^Pasal\s+(\d+[A-Z]?)(?:\s*$|\s+(?=[A-Z][a-z]))", _M)`.
2. **`is_amendment` false positive** — `_RE_AMENDMENT.search(text)` men-scan seluruh
   body, salah trigger ketika PENJELASAN mengutip UU amandemen. Fix: scope pencarian
   cuma ke baris pertama (judul dokumen).
3. **Mid-line section headers** — marker PENJELASAN ATAS dan LAMPIRAN muncul di
   tengah baris ketika page break PDF tidak terpreservasi sebagai newline. Fix:
   preprocessing step `_normalize_pdf_lines()` di `_segment()`.

### 9. Retrieval timeout — axios default 30s terlalu pendek
`retrieveChunks()` di `frontend/src/services/api.js` pakai override timeout 120s
(default global axios 30s). Model retrieval (`intfloat/multilingual-e5-large`) warm-up
saat startup via FastAPI `lifespan` context di `backend/main.py` — kalau timeout
default dipakai, request pertama sering 504 sebelum model selesai load.
