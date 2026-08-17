# Issues

## Terbuka

| # | Prioritas | Issue | Owner | Catatan |
|---|---|---|---|---|
| I-2 | P3 | 10 test `TestTokenAwareChunker` (+ `test_chunk_token_strategy`) ERROR lokal karena SSL/tiktoken gagal download `cl100k_base` dari `openaipublic.blob.core.windows.net` — diblok proxy korporat. | n/a (environment-specific) | Bukan bug kode — semua 137 test lulus di CI (GitHub Actions, tidak di belakang proxy yang sama). Tidak actionable tanpa akses jaringan berbeda. |

## Ditutup

| # | Tanggal | Issue | Resolusi |
|---|---|---|---|
| I-1 | 2026-08-17 | Moderate/low severity npm (frontend) & pip (backend) vulnerabilities belum diaudit — CI cuma gate `npm audit --production --audit-level=high` dan `pip-audit` default ke `backend/requirements.txt` saja. | Full audit dijalankan, semua severity, semua manifest: `npm audit` (frontend, tanpa `--production`/`--audit-level`, termasuk devDependencies) → 0 vulnerabilities. `pip-audit --requirement backend/requirements.txt` → 0. `pip-audit --requirement requirements-retrieval.txt` (root, tidak pernah di-gate CI sama sekali) → 0. Kesimpulan: tidak ada temuan tersembunyi di bawah threshold high — gap CI (I-0 lama) ternyata tidak menyembunyikan risiko nyata saat ini. Kebijakan severity gate CI tetap jadi pending decision (docs/DECISIONS.md) untuk ke depannya, bukan karena ada temuan mendesak. |
| I-3 | 2026-08-17 | Lint workflow merah di master selama 21 hari (`ruff check backend/` → 37 errors) | Root cause: `pip install ruff black mypy` unpinned di `lint.yml`, CI resolve ke ruff 0.16.0 dengan default rule set lebih luas. Fixed via `ruff --fix` (32 mekanis) + 6 `noqa: BLE001` justified (boundary service eksternal) + tool version dipin. Commit `174a501`. |
| I-4 | 2026-08-17 | axios 1.16.0 & js-yaml 4.3.0 (frontend) kena CVE high-severity baru | Bump ke axios 1.19.0 / js-yaml 4.3.1 via `npm audit fix`, dalam semver range existing. Commit `b471b93`. |
| I-5 | 2026-08-17 | 68 Dependabot alert terbuka (25 high) | Root cause: root `package-lock.json` orphan sejak sebelum Electron dihapus (masih ngunci electron-builder toolchain lama) — 45 alert. Plus 10 alert mis-atribusi GitHub dependency-graph untuk `mistune` di `requirements-retrieval.txt` (file itu tidak pernah deklarasi mistune). Lockfile diregenerate bersih (commit `e3f9511`); 10 alert mis-atribusi di-dismiss via API reason `inaccurate`. Hasil: 0 open alert. |
| I-6 | 2026-07-26 | `mistune` 3.2.1 kena 19 CVE (CVE-2026-59922–59930 dkk) | Bump ke `mistune==3.3.4`. Perlu narrowing type tambahan di `markdown_struct.py` untuk mypy (lihat docs/GOTCHAS.md #7). |
| I-7 | 2026-06-29 | `form-data` CRLF injection, `js-yaml` quadratic DoS, `esbuild` dev server cross-origin | Patch form-data; bump `vite` 5→8 dan `@vitejs/plugin-react` 4→6 (resolve esbuild transitively). |
| I-8 | 2026-05-02 | mypy CI: 8 type error tidak terdeteksi (`\|\| true` di workflow); bandit CI scan `backend/.venv` dan pakai `--exit-zero` | mypy: 8 error diperbaiki, `\|\| true` dihapus (enforced). bandit: exclude `backend/.venv`, `--exit-zero` dihapus (zero high-severity findings enforced). Bagian dari Phase 1 cleanup. |
