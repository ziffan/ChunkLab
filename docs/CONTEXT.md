# Context

Status terkini di atas, riwayat di bawah (reverse-chronological). Baca entri teratas
dulu untuk tahu "kita di mana".

## 2026-09-22 — Security Scan merah 2 minggu diperbaiki, `AGENTS.md` jadi symlink

**Status:** v0.2.4. Security Scan (`security.yml`) merah di master sejak 2026-09-13
(2 run berturut-turut), fixed. Dependabot alert naik 0 → 4 selama repo idle ~5 minggu
sejak 2026-08-17; keempatnya tertutup oleh satu `npm audit fix` di `frontend/`.

**Yang dikerjakan:**
- Security Scan merah 2 minggu — failing step `npm audit --production --audit-level=high`.
  Root cause satu temuan produksi: `js-yaml 4.0.0–4.3.1` (GHSA-2883-xcg3-v3hh, high),
  dipakai `ExportButton.jsx` untuk export YAML. Fix non-breaking karena `js-yaml 4.3.2`
  masuk range `^4.1.1` — `npm audit fix` menutup keempat alert sekaligus. Detail:
  docs/ISSUES.md I-9.
- **Temuan proses:** gate CI pakai `--production`, jadi CVE high di devDependency chain
  tidak pernah menembus gate — CI hijau sementara Dependabot menumpuk. Dicatat sebagai
  docs/GOTCHAS.md #11 (termasuk perintah `gh api` untuk cek alert langsung).
- `AGENTS.md` diganti dari pointer file 23-byte jadi symlink asli ke `CLAUDE.md`
  (git mode `120000`). Butuh `core.symlinks=true` — docs/GOTCHAS.md #10. Commit `b05710c`.
- **Kebijakan gate keamanan dependency diputuskan** — keluar dari Pending, dua entri
  Locked baru di docs/DECISIONS.md. Gate npm jadi asimetris: production tree semua
  severity, devDependency high+. Semantiknya diverifikasi dengan advisory low asli
  (`postcss-selector-parser@6.1.2` → `--omit=dev` exit 1, `--audit-level=high` exit 0),
  bukan diasumsikan dari dokumentasi.
- `requirements-retrieval.txt` ternyata **permukaan produksi** — `backend/Dockerfile:20-21`
  meng-`pip install`-nya ke image, resolve ke 42 paket termasuk `torch`, `transformers`,
  `huggingface-hub`, dan CI tidak pernah mengauditnya sekali pun. Sekarang diaudit
  `pip-audit` + di-pin penuh ke resolusi Linux (manylinux x86_64, CPython 3.12).
  Verifikasi: re-resolve file terpin → set **identik** (42 masuk, 42 keluar).
- `security.yml`: `bandit` dan `pip-audit` di-pin versinya. Sebelumnya keduanya
  `pip install` unpinned — melanggar aturan JANGAN PERNAH repo ini sendiri, dan persis
  kelas kegagalan yang membuat Lint merah 21 hari (I-3).
- Push ke `origin` (`406180a..58b5275`). Kelima workflow hijau (Security Scan, Docker
  Build, Test, Lint, Graph Update) dan 4 Dependabot alert auto-close → 0. Docker Build
  sekaligus memverifikasi manifest retrieval yang di-pin benar-benar terinstal di image
  Linux (layer `RUN pip install -r requirements-retrieval.txt` dieksekusi, bukan cache).
- Dua run Security Scan merah — keduanya commit lama `406180a` (pre-fix), termasuk satu
  re-run manual terhadap kode lama — dihapus dari Actions atas permintaan owner supaya
  tab Actions bersih (sekarang 0 non-success). Dicatat sebagai catatan integritas di
  docs/ISSUES.md I-9, karena record-nya jadi tidak bisa diverifikasi lagi.

**Belum selesai:**
- Tidak ada item teknis yang menggantung. Dua hal yang tadi ditandai "belum" sudah
  tertutup: push selesai dan terverifikasi, dan pin manifest retrieval terbukti
  terinstal di image Linux lewat Docker Build. Sisa pekerjaan adalah tiga pending
  decision di `docs/DECISIONS.md` (Dependabot config, `ruff.toml`/`pyproject.toml`,
  tooling lockfile Python) — semuanya punya owner + deadline, tidak ada yang lewat.

**Next step (urutan disarankan):**
1. Verifikasi terjadwal: run cron Security Scan berikutnya (Minggu 2026-09-27 00:00 UTC)
   akan jadi kali pertama workflow yang baru berjalan terjadwal, bukan lewat push.
   Harus hijau — kalau tidak, bedanya ada di `schedule` event, bukan di step-nya.
2. Pending decision: aktifkan `.github/dependabot.yml` (deadline 2026-10-31) — repo ini
   tidak punya sama sekali, dan itulah kenapa 4 alert cuma jadi notifikasi yang tidak
   dilihat siapa pun selama ~5 minggu.
3. Pending decision: `pyproject.toml`/`ruff.toml` untuk pin rule-set ruff
   (docs/GOTCHAS.md #6).
4. Pending decision: tooling lockfile Python (`pip-compile`/`uv`) menggantikan pin
   manual 42 baris di `requirements-retrieval.txt` — deadline berupa trigger: sebelum
   bump dependency pertama di file itu.

---

## 2026-08-17 — CI hijau lagi, Dependabot bersih, repo lokal dirapikan

**Status:** v0.2.3. Semua 4 GitHub Actions workflow (Lint, Test, Security Scan, Docker
Build) hijau di `master`. 0 open Dependabot alert (dari 68). Repo lokal 1.4GB → 99MB
setelah bersih-bersih artifact mati. Full dependency audit (semua severity, semua
manifest — bukan cuma yang di-gate CI) sudah dijalankan: 0 temuan di frontend maupun
backend, termasuk `requirements-retrieval.txt` yang CI tidak pernah cek sama sekali.

**Yang dikerjakan:**
- Lint CI (merah 21 hari) — fixed, root cause unpinned ruff/black/mypy. Detail:
  docs/ISSUES.md I-3, docs/DECISIONS.md (pin tool versions).
- axios/js-yaml CVE baru di frontend — dipatch. docs/ISSUES.md I-4.
- 68 Dependabot alert — 45 dari root `package-lock.json` orphan (diregenerate bersih),
  10 dari mis-atribusi mistune (di-dismiss). docs/ISSUES.md I-5,
  docs/DECISIONS.md (root lockfile locked nol-dependency).
- Full dependency audit (moderate/low severity, semua manifest) — 0 temuan.
  docs/ISSUES.md I-1 (closed).
- Local cleanup: hapus `dist_electron/`, `build/`, `dist/`, `backend.spec` (~1.8GB,
  sisa Electron/PyInstaller, 0 referensi di source), `backend/.venv` (~1GB, basi 4
  bulan). `internal_use/` dan `frontend/node_modules` dipertahankan (masih dipakai).
- Docs direstrukturisasi: status/gotcha/decision/issue yang tadinya numpuk di
  `CLAUDE.md` dan `CHANGELOG.md` dipecah ke `docs/CONTEXT.md` (file ini),
  `docs/GOTCHAS.md`, `docs/DECISIONS.md`, `docs/ISSUES.md`. `CLAUDE.md` diramping jadi
  pointer + panduan kerja permanen (Commands/Architecture/Env/Docker/Key Constraints).
  `CHANGELOG.md` tetap terpisah sebagai release notes standar OSS (Keep a Changelog).

**Belum selesai:** Tidak ada item aktif tersisa dari sesi ini.

**Next step (urutan disarankan):**
1. Putuskan docs/DECISIONS.md (Pending): perlu `pyproject.toml`/`ruff.toml` untuk pin
   rule-set ruff + fix gotcha cwd-dependent import-sort (docs/GOTCHAS.md #6)?
2. Putuskan docs/DECISIONS.md (Pending): kebijakan severity gate CI (`npm audit`/
   `pip-audit` cuma gate high+) — audit manual 2026-08-17 tidak menemukan apa-apa di
   bawah threshold saat ini, tapi kebijakan ke depan (apakah perlu di-gate lebih ketat,
   atau audit `requirements-retrieval.txt` masuk CI juga) belum diputuskan.

---

## 2026-07-26 — Security patch round + mypy fix

`mistune` `3.0.2 → 3.3.4` (19+ CVE), `axios` `1.15.0 → 1.16.0`. Butuh type-narrowing
tambahan di `markdown_struct.py` untuk mypy (docs/GOTCHAS.md #7) karena mistune 3.3.4
mengekspos return type baru untuk `md(text)`.

---

## 2026-06-29 — Patch form-data/js-yaml/esbuild, vite 5→8

`form-data` CRLF injection, `js-yaml` quadratic DoS, `esbuild` dev-server cross-origin
(resolved via `vite` 5→8, `@vitejs/plugin-react` 4→6).

---

## 2026-05-02 — v0.2.0: Phase 1–3 cleanup selesai

Phase 1 (CI hardening: mypy 8 error fixed & enforced, bandit exclude `.venv` & enforced
zero-high) → Phase 2 (Electron dihapus, `sentence` strategy digabung ke `sentence_id`,
`RETRIEVAL_MODEL` env var configurable) → Phase 3 (docs restructure: `docs/strategies.md`,
`docs/architecture.md`, README slim, CHANGELOG cleanup). Docker Compose support
ditambahkan. Retrieval Simulation diuji end-to-end di Docker. 137 test passing (127
lokal — 10 `TestTokenAwareChunker` skip karena SSL/tiktoken diblok proxy korporat,
lihat docs/ISSUES.md I-2).

Git history di-rewrite sekali (`git filter-repo --replace-text`, force-push) untuk
membersihkan alamat email sebelum repo dibuka jadi OSS (lihat docs/DECISIONS.md
JANGAN PERNAH).

---

## 2026-04-30 — v0.1.0: Initial feature-complete release

6 chunking strategy (`fixed`, `recursive`, `token`, `sentence_id`, `markdown`,
`legal_id`), quality metrics (BQ/ID/trun), Retrieval Simulation, export (JSON/JSONL/YAML),
regex metadata extraction, token estimation multi-provider (OpenAI/Ollama/LM
Studio/OpenRouter/Gemini/Mock). Detail lengkap: `CHANGELOG.md` [0.1.0].
