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

## Git / symlink repo

### 10. `AGENTS.md` adalah symlink asli — butuh `core.symlinks=true`
`AGENTS.md` tersimpan di git sebagai symlink (mode `120000`) menunjuk ke `CLAUDE.md`,
supaya agent yang baca `AGENTS.md` (Codex/OpenCode/Cursor) melihat isi identik tanpa
harus mengikuti instruksi pointer. Sebelumnya file ini adalah pointer 23-byte
`read /CLAUDE.md in full` — sudah diganti.

**Kenapa rapuh:** kalau `core.symlinks=false` (default git di Windows tanpa Developer
Mode), checkout menulis `AGENTS.md` sebagai **file teks biasa berisi string
`CLAUDE.md`** — bukan link, dan bukan instruksi. Agent yang baca file itu tidak dapat
apa-apa.

**Symptom:** `git ls-files -s AGENTS.md` menunjukkan `100644` (bukan `120000`), atau
`Get-Item AGENTS.md` tidak menampilkan `LinkType: SymbolicLink`.

**Fix (Windows, Developer Mode ON — tidak perlu admin):**
```powershell
git config core.symlinks true      # repo-local, jangan --global
Remove-Item AGENTS.md -Force
cmd /c mklink AGENTS.md CLAUDE.md
git checkout -- AGENTS.md          # verifikasi git bisa recreate link
```

Jangan pakai `ln -s` dari Git Bash — di MSYS tanpa dukungan symlink native, perintah
itu **menyalin** file dan exit 0 tanpa warning, jadi dua file terpisah yang akan
drift. Pakai `cmd /c mklink` dari PowerShell.

**Jangan "perbaiki" `AGENTS.md` dengan menulis ulang jadi file berisi pointer** — itu
mengembalikan symlink jadi file biasa (`100644`) dan merusak sinkronisasi.

**Catatan:** `core.symlinks` di-set repo-local, bukan global. Clone baru di mesin
Windows perlu `git config core.symlinks true` sebelum checkout, atau clone dengan
`git clone -c core.symlinks=true`. Di Linux (CI, VPS) symlink bekerja native tanpa
config tambahan.

## CI / dependency

### 11. Gate `npm audit --production` buta terhadap devDependency — CI hijau ≠ Dependabot bersih
`security.yml` menjalankan `npm audit --production --audit-level=high` di `frontend/`.
Flag `--production` membatasi audit ke production tree saja, jadi CVE **high** di
devDependency chain (vite/postcss/tailwind → `browserslist`,
`baseline-browser-mapping`, `postcss-selector-parser`) **tidak pernah menembus gate**.
CI bisa hijau berminggu-minggu sementara Dependabot alert menumpuk.

**Symptom:** CI Security Scan hijau tapi jumlah open Dependabot alert naik. Atau
sebaliknya: CI merah hanya karena satu paket produksi, padahal alert yang terbuka
lebih banyak (2026-09-22: 4 alert, hanya `js-yaml` yang menembus gate).

**Implikasi:** jangan pakai "CI hijau" sebagai bukti dependency bersih. Kalau repo
idle beberapa minggu, **cek Dependabot alert langsung** sebagai langkah pertama —
itu satu-satunya sinyal yang mencakup devDependency:

```bash
gh api "repos/ziffan/ChunkLab/dependabot/alerts?state=open&per_page=50" \
  --jq '.[] | "\(.security_advisory.severity)\t\(.dependency.package.name)\t\(.dependency.manifest_path)"'
```

**Fix:** `npm audit fix` (tanpa `--force`) menutup devDependency chain juga, selama
versi patch-nya masih dalam range semver yang dideklarasikan. Verifikasi dengan
**dua** gate, bukan satu:

```bash
NODE_OPTIONS=--use-system-ca npm audit --production --audit-level=high  # gate CI
NODE_OPTIONS=--use-system-ca npm audit                                  # termasuk devDeps
```

Kebijakan apakah devDependency severity perlu di-gate di CI masih pending decision —
lihat `docs/DECISIONS.md`.

## Bash tool / Node

### 12. Node tidak bisa membaca `/tmp` milik Bash tool — di-resolve jadi `D:\tmp`
Bash tool (Git Bash/MSYS) memetakan `/tmp` ke direktori temp MSYS, tapi `node` yang
dijalankan dari shell yang sama **tidak** MSYS-aware: `fs.readFileSync('/tmp/x.json')`
di-resolve jadi `D:\tmp\x.json` dan gagal. Shell redirect (`> /tmp/x.json`) tetap
berhasil menulis, jadi file-nya benar-benar ada — yang salah cuma cara node membacanya.
Menyesatkan karena errornya terbaca seperti "file tidak jadi ditulis".

**Symptom:** `ls -la /tmp/x.json` menunjukkan file ada dan berisi, tapi node gagal
`ENOENT: no such file or directory, open 'D:\tmp\x.json'`.

**Fix:** alirkan lewat stdin, jangan lewat path.

```bash
node -e "const j=JSON.parse(require('fs').readFileSync(0,'utf8')); /* ... */" < /tmp/x.json
```

`readFileSync(0)` membaca stdin dan tidak bergantung pada pemetaan path MSYS. Berlaku
juga untuk `python -c` yang menerima path `/tmp` sebagai argumen.
