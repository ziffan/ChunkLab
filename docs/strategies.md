# Chunking Strategies

## Panduan Pemilihan Strategi

| Strategi | Cocok untuk | Hindari jika |
|---|---|---|
| **Fixed Size** | Baseline cepat; teks homogen tanpa struktur khusus | Teks punya struktur paragraf/kalimat yang harus dipertahankan |
| **Recursive Character** | Teks umum berbahasa apapun; menghormati batas paragraf dan kalimat secara bertahap | Dokumen hukum terstruktur atau teks markdown berhierarki tinggi |
| **Token Aware** | Pipeline yang ketat terhadap batas token (misal GPT-4 8K, Claude 100K) | Teks sangat pendek; overhead tiktoken tidak sepadan |
| **Sentence (sentence_id)** | Teks berbahasa Indonesia atau 23 bahasa lain yang didukung pysbd | Dokumen hukum berstruktur — gunakan `legal_id` |
| **Legal Indonesia** | Peraturan UU/PP/Perpres/Perda; chunk di batas Pasal atau BAB | Teks non-hukum; tidak ada penanda "Pasal N" |
| **Markdown Structure** | Dokumentasi teknis, README, artikel berhierarki header | Teks plain tanpa heading; akan menghasilkan satu chunk besar |

## Metadata Otomatis: Strategi `legal_id`

Strategi `legal_id` menganalisis struktur dokumen UU/PP/Perpres/Perda secara otomatis dan menyematkan metadata berikut pada setiap chunk — **tanpa perlu menambahkan regex pattern apapun**:

| Field | Tipe | Contoh Nilai |
|---|---|---|
| `_legal_path` | `string` | `"BAB I > Bagian Kedua > Pasal 5"` |
| `_legal_number` | `string` | `"5"` (nomor Pasal atau BAB) |
| `_legal_section` | `string` | `"BATANG_TUBUH"` |
| `_legal_unit` | `string` | `"pasal"` atau `"bab"` |

### Section dokumen yang dikenali

| Nilai `_legal_section` | Isi |
|---|---|
| `JUDUL` | Judul peraturan sebelum Menimbang |
| `PEMBUKAAN` | Menimbang · Mengingat · Memutuskan · Menetapkan |
| `BATANG_TUBUH` | Isi pasal-pasal utama |
| `PENJELASAN` | Penjelasan umum + Pasal Demi Pasal |
| `LAMPIRAN` | Lampiran I, II, dst. |

### Hierarki yang dikenali dalam BATANG_TUBUH

```
BAB I
  └─ Bagian Kesatu
       └─ Paragraf 1
            └─ Pasal 1
                 └─ (1) ayat  ← konten di dalam chunk, tidak di-split lebih lanjut
```

Semua level hierarki yang aktif digabung menjadi `_legal_path`. Untuk dokumen UU perubahan (mengandung "PERUBAHAN ... ATAS UNDANG-UNDANG"), nomor Pasal dalam angka Romawi juga dikenali secara otomatis.

### Regex yang tidak perlu ditambahkan manual

| Pattern | Kenapa tidak perlu |
|---|---|
| `BAB\s+[IVXLCDM]+` | Ada di `_legal_path` |
| `Pasal\s+\d+` | Ada di `_legal_number` dan `_legal_path` |
| `Bagian\s+Kes\w+` | Ada di `_legal_path` |
| `Paragraf\s+\d+` | Ada di `_legal_path` |

### Regex yang masih berguna (metadata tambahan)

| Tujuan | Pattern |
|---|---|
| Nomor peraturan | `Nomor\s+\d+\s+Tahun\s+\d{4}` |
| Referensi UU lain | `UU\s*(?:No\.?\s*)?\d+\s*(?:Tahun\s*)?\d{4}` |
| Tanggal | `\d{1,2}\s+\w+\s+\d{4}` |
| Huruf ayat | `huruf\s+[a-z]` |

> Contoh pattern lengkap tersedia di panel **Buka Referensi Regex → Contoh: Regulasi Indonesia** di dalam aplikasi.

## Estimasi Token — Catatan per Provider

| Provider | Metode | Status Pengujian | Catatan |
|---|---|---|---|
| **Ollama** | `/api/tokenize` (native) → tiktoken proxy | ✅ Diuji (lokal) | Lihat catatan di bawah |
| **OpenAI** | tiktoken `cl100k_base` | ⚠️ Belum diuji | Akurat untuk GPT-4, GPT-3.5, model berbasis cl100k |
| **OpenRouter** | tiktoken `cl100k_base` | ⚠️ Belum diuji | Routing ke berbagai model; akurasi bergantung model tujuan |
| **LM Studio** | tiktoken `cl100k_base` | ✅ Diuji (lokal) | Endpoint kompatibel OpenAI |
| **Gemini** | Estimasi char/4 | ⚠️ Belum diuji | API tokenizer Gemini memerlukan autentikasi — belum diintegrasikan |
| **Mock** | Estimasi char/4 | ✅ | Aktif saat `MOCK_MODE=true` atau provider tidak tersedia |

> Fitur estimasi token hanya diuji secara langsung dengan **Ollama lokal**. Provider lain menggunakan jalur kode yang sama tetapi belum diverifikasi dengan API key nyata.

### Ollama — `/api/tokenize` dan fallback

Endpoint `/api/tokenize` baru tersedia di **Ollama 0.3.x ke atas**. Pada versi lebih lama, ChunkLab otomatis jatuh ke tiktoken `cl100k_base` sebagai proxy:

- Hasilnya tetap akurat secara praktis — kebanyakan model modern (Qwen, Llama, Mistral, Gemma) menggunakan BPE dengan kosakata yang mirip cl100k.
- Untuk teks hukum Indonesia, rasio aktual sekitar **2.5 karakter per token** (bukan 4 seperti teks Inggris). Gunakan panduan: target 512 token → ~1100 chars, target 1024 token → ~2500 chars.
- Banner **MOCK** **tidak** muncul karena ini bukan estimasi kasar (bukan char/4).

**Model yang valid untuk estimasi token:** gunakan model LLM generatif (contoh: `qwen3.5:4b`, `llama3.2:3b`, `qwen2.5-coder:7b`).

> **Model embedding tidak bisa dipakai untuk token counting** — model seperti `bge-m3`, `nomic-embed-text`, atau `qwen3-embedding` tidak memiliki endpoint tokenisasi yang kompatibel. Gunakan model LLM.

### Mengaktifkan tokenizer nyata

Set `MOCK_MODE=false` di `backend/.env` lalu restart backend:

```env
MOCK_MODE=false
```
