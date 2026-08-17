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
| Kebijakan severity Dependabot/CI: `npm audit`/`pip-audit` di CI cuma gate di high+, dan `security.yml` tidak pernah audit root `requirements-retrieval.txt` sama sekali. Apakah moderate/low perlu di-gate juga, dan apakah `requirements-retrieval.txt` perlu masuk `pip-audit` di CI? | belum ditentukan | belum ada | Audit manual penuh dijalankan 2026-08-17 (docs/ISSUES.md I-1, closed) — 0 temuan di semua severity/manifest saat ini, jadi tidak mendesak, tapi gap kebijakannya (apa yang di-gate CI) masih belum diputuskan untuk ke depan. |

## Change Log (obsolete / superseded)

- ~~Electron sebagai desktop packaging path~~ — superseded oleh web-only + Docker
  Compose (lihat Locked di atas), `0.2.0`.
- ~~`sentence` sebagai strategy terpisah dari `sentence_id`~~ — superseded, digabung
  `0.2.0`.
