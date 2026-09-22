# Decisions

Locked / pending / never — struktural decisions untuk ChunkLab. Locked jangan diubah
tanpa revisit eksplisit (lihat CLAUDE.md § Decision Discipline). Keputusan yang
di-supersede masuk Change Log di bawah, tidak dihapus.

## Locked

### Electron dihapus — web-only, Docker Compose adalah deployment path
**Context:** ChunkLab awalnya punya dual surface (Electron desktop + web). Maintenance
ganda untuk sandbox/testing tool tidak sepadan.
**Decision:** Electron dihapus total (`0.2.0`, Phase 2.1). App web-only; `docker compose
up --build` adalah cara deploy yang direkomendasikan.
**Consequences:** `electron/main.js`, PyInstaller (`backend.spec`), dan build artifacts
(`dist_electron/`, `build/`, `dist/`) jadi dead — sudah dibersihkan dari disk lokal
(2026-08-17). Root `package.json` sekarang punya nol dependency (cuma
`postinstall: cd frontend && npm install`).
**Alternatives rejected:** Pertahankan Electron sebagai opsi packaging tambahan —
ditolak, tidak sepadan untuk sandbox tool dengan base user kecil.

### `sentence` strategy dihapus, digabung ke `sentence_id`
**Context:** Dua chunker terpisah (`sentence`, `sentence_id`) tumpang tindih fungsinya.
**Decision:** `sentence` dihapus; semua fungsionalitas masuk `sentence_id`, dengan
`pysbd` sebagai optional dependency (23 bahasa) dan fallback ke regex splitter
Indonesia kalau `pysbd` tidak terpasang atau bahasa tidak didukung.
**Consequences:** `CHUNKER_REGISTRY` sekarang 6 strategy (bukan 7): `fixed`,
`recursive`, `token`, `sentence_id`, `markdown`, `legal_id`.
**Alternatives rejected:** Pertahankan keduanya sebagai alias — ditolak, membingungkan
untuk API konsumen tanpa manfaat nyata.

### Root `package.json`/`package-lock.json` tetap nol dependency
**Context:** Lockfile root sempat jadi orphan ~4 bulan (masih ngunci electron-builder
toolchain lama) setelah Electron dihapus tapi `package.json` tidak pernah di-audit
ulang — jadi sumber 45 dari 68 Dependabot alert (2026-08-17).
**Decision:** Root package.json/lockfile tidak boleh punya dependency nyata lagi.
Kalau butuh tooling root-level di masa depan, evaluasi dulu apakah bisa hidup di
`frontend/` saja.
**Consequences:** Setiap kali Dependabot/npm audit flag sesuatu di `package-lock.json`
(bukan `frontend/package-lock.json`), itu tanda lockfile root sudah "dikotori" lagi —
investigasi kenapa sebelum patch.

### CI lint tool versions (`ruff`/`black`/`mypy`) di-pin exact di `lint.yml`
**Context:** `pip install ruff black mypy` tanpa pin di CI diam-diam resolve ke ruff
0.16.0 dengan default rule set lebih luas dari kode yang ditulis — Lint merah 21 hari
tanpa ada yang sadar (2026-08-17).
**Decision:** Pin `ruff==0.16.0 black==26.5.1 mypy==2.3.0` (atau versi lebih baru yang
sudah diverifikasi lulus) di `.github/workflows/lint.yml`, bukan biarkan `pip install`
ambil latest.
**Consequences:** Upgrade tool linting sekarang butuh langkah eksplisit (bump versi +
jalankan lint lokal sebelum commit), bukan otomatis. Trade-off diterima demi CI yang
predictable.
**Alternatives rejected:** Biarkan unpinned dan andalkan review manual tiap kali CI
merah — sudah terbukti gagal (21 hari tidak ketahuan).

### Gate keamanan dependency di CI bersifat asimetris (prod semua severity, devDep high+)
**Context:** `security.yml` memakai satu gate `npm audit --production --audit-level=high`,
dan kombinasi `--production` + ambang `high` membuatnya buta terhadap devDependency
sama sekali. Blind spot itu terbukti bocor pada 2026-09-22 (docs/ISSUES.md I-9): 4
Dependabot alert menumpuk selama repo idle ~5 minggu, dan **3 di antaranya tidak
pernah terlihat CI** — termasuk `browserslist` yang high. Kelas rot ini sudah pernah
terjadi dua kali di repo ini (I-3 lint merah 21 hari, I-5 68 alert numpuk).
Frontend production tree cuma 4 dependency langsung (butuh waktu 5 minggu untuk
menghasilkan 1 advisory), sementara devDependency tree ~120 paket lewat chain
vite/tailwind/postcss yang data-package-nya (`browserslist`, `caniuse-lite`,
`electron-to-chromium`) rilis nyaris mingguan.
**Decision:** Dua gate terpisah di `security.yml`: `npm audit --omit=dev` tanpa
`--audit-level` (production tree, **semua** severity — default npm adalah `low`), dan
`npm audit --audit-level=high` (seluruh tree, jadi devDependency ikut ter-gate di high+).
**Consequences:** Production tree ter-gate ketat — masuk akal karena kecil dan CVE-nya
user-facing (`js-yaml` DoS mempengaruhi app yang jalan). DevDependency ter-gate di high
saja — cukup untuk menangkap `browserslist` dan `js-yaml`, tanpa merah permanen dari
DoS build-tool yang tidak pernah ikut terkirim. Konsekuensi negatif yang diterima:
medium/low di devDependency chain tetap tidak ter-gate CI dan hanya muncul sebagai
Dependabot alert — jadi "CI hijau" **masih bukan** bukti dependency bersih
(docs/GOTCHAS.md #11). Semantik kedua gate diverifikasi 2026-09-22 dengan advisory low
asli (`postcss-selector-parser@6.1.2`): `--omit=dev` → exit 1, `--audit-level=high` → exit 0.
**Alternatives rejected:** (a) Status quo `--production --audit-level=high` — ditolak,
sudah terbukti bocor. (b) Hapus `--production` saja tanpa step kedua — ditolak, tetap
buta ke medium/low di production tree, padahal tree-nya kecil dan murah di-gate penuh.
(c) Semua severity di mana pun — ditolak, menukar satu mode kegagalan (merah yang tidak
dilihat) dengan mode lain: merah permanen yang diabaikan, yang justru melatih orang
mengabaikan CI.

### `requirements-retrieval.txt` adalah permukaan produksi — diaudit CI dan di-pin penuh
**Context:** Manifest ini sebelumnya tidak pernah diaudit CI sama sekali. Verifikasi
2026-09-22 menunjukkan itu salah kategori: `backend/Dockerfile:20-21` meng-`pip install`
file ini ke image produksi, dan resolusi Linux-nya menarik **42 paket** termasuk
`torch`, `transformers`, `huggingface-hub`, `scipy`, `scikit-learn` — permukaan
dependency terbesar di repo ini (bandingkan `backend/requirements.txt`: 9 paket).
Isinya dulu `>=` lower bounds, jadi setiap build Docker me-resolve ulang ke versi
terbaru: image yang jalan memuat set berbeda dari yang diaudit, dan patch upstream
(baik maupun berbahaya) masuk tanpa langkah yang bisa ditinjau.
**Decision:** `requirements-retrieval.txt` diaudit `pip-audit` di `security.yml`, dan
di-pin penuh dengan `==` untuk seluruh 42 paket hasil resolusi `python:3.12-slim`
(CPython 3.12, manylinux x86_64). Dua dependency langsung (`sentence-transformers`,
`numpy`) ditandai terpisah dari transitive.
**Consequences:** Versi yang diaudit = versi yang diinstal, dan rebuild image jadi
deterministik. Konsekuensi negatif yang diterima: patch keamanan upstream pada 42 paket
itu tidak lagi masuk otomatis — bump harus dilakukan sengaja, dan gate audit-lah yang
memberi tahu kapan. File ini sekarang harus di-regenerate, bukan diedit sebagian
(prosedurnya ada di header file). Verifikasi 2026-09-22: file terpin di-resolve ulang
untuk target Linux menghasilkan set **identik** (42 masuk, 42 keluar, tidak ada yang
mengapung atau hilang) — artinya pin-nya lengkap dan saling-konsisten. `pip-audit`
terhadap file terpin → exit 0. **Belum diverifikasi:** build image Docker sungguhan
(daemon Docker tidak jalan saat itu) — CI Docker Build akan jadi verifikasi pertama.
**Alternatives rejected:** (a) Biarkan `>=` dan andalkan `pip-audit` — ditolak, gate-nya
jadi mengukur resolusi hari ini sementara image bisa memuat resolusi bulan lalu.
(b) Pin hasil resolusi Windows — ditolak, resolusi Linux menarik set berbeda
(`packaging`, `setuptools`) dan `torch` punya wheel platform-specific. (c) Hanya pin dua
dependency langsung — ditolak, transitive (torch/transformers/huggingface-hub) justru
bagian yang paling sering kena CVE. (d) Pakai `pip-compile`/`uv` — ditunda, bukan
ditolak; lihat Pending.

## JANGAN PERNAH

- **Jangan rename `CLAUDE.md` → `AGENTS.md`.** Claude Code membaca nama file
  `CLAUDE.md` secara spesifik; rename akan membuat instruksi project tidak terbaca
  otomatis lagi.
- **Jangan biarkan `pip install`/`npm install` tool CI tanpa pin versi** di workflow
  manapun (lint, security, test) — lihat Locked di atas, sudah terbukti menyebabkan
  regresi diam-diam.
- **Jangan hapus/reformat history git repo ini tanpa alasan kuat** — history pernah
  di-rewrite sekali (`git filter-repo --replace-text`, prepare-OSS-release) untuk
  membersihkan alamat email; force-push seperti itu berisiko dan sudah dilakukan
  sekali, tidak perlu diulang kecuali insiden serupa.

## Pending

| Keputusan | Owner | Deadline | Catatan |
|---|---|---|---|
| Tambah `pyproject.toml`/`ruff.toml` untuk pin rule-set ruff eksplisit (bukan cuma versi tool) | belum ditentukan | belum ada | Juga akan memperbaiki docs/GOTCHAS.md #6 — tanpa config file, deteksi known-first-party ruff bergantung pada cwd saat invoke, bukan cuma target path. |
| Pakai tooling lockfile Python (`pip-compile` / `uv pip compile`) menggantikan pin manual di `requirements-retrieval.txt` | ziffan | sebelum bump dependency pertama di file itu | Pin manual 42 baris tidak membedakan mana transitive dari mana dan setiap bump harus diedit tangan sambil menjaga set tetap konsisten (lihat header file untuk prosedur regenerate). Tooling lockfile menghasilkan file itu dari intent, plus `--upgrade-package` untuk bump bertarget. Ditunda — bukan ditolak — karena menambah toolchain baru (CI + dev) untuk repo yang belum punya. |
| Aktifkan `.github/dependabot.yml` untuk PR update otomatis | ziffan | 2026-10-31 | Repo ini **tidak punya** config Dependabot, jadi alert cuma jadi notifikasi dependency graph — tidak ada PR otomatis yang memperbaikinya. I-9 terjadi justru karena tidak ada yang melihat alert itu selama ~5 minggu. Trade-off: PR otomatis menambah noise, dan repo ini sudah punya pengalaman buruk dengan lockfile yang "dikotori" (lihat Locked, root lockfile nol dependency) — jadi perlu diputuskan apakah security-only, atau security + version. |

## Change Log (obsolete / superseded)

- ~~Electron sebagai desktop packaging path~~ — superseded oleh web-only + Docker
  Compose (lihat Locked di atas), `0.2.0`.
- ~~`sentence` sebagai strategy terpisah dari `sentence_id`~~ — superseded, digabung
  `0.2.0`.
