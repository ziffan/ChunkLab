# Rencana: Panel Referensi Regex di Frontend

## Lokasi

Di dalam panel "Regex Patterns", di bawah teks penjelasan singkat yang sudah ada, tambahkan tombol toggle **"Buka Referensi"**. Saat diklik, muncul tabel referensi regex yang bisa di-collapse lagi.

## UI Layout

```
┌─ Regex Patterns ────────────── [+] ─┐
│ Gunakan regex Python standar...      │
│ Tekan [T] untuk menguji pola...      │
│                                      │
│ ▶ Buka Referensi Regex         (toggle) │
│                                      │
│ ┌─ Karakter Umum ──────────────────┐ │
│ │ \s  Spasi putih   Pasal\s+\d+    │ │
│ │ \d  Digit 0-9     \d{4} → 2024   │ │
│ │ ...                               │ │
│ └───────────────────────────────────┘ │
│ ┌─ Kuantifier ─────────────────────┐ │
│ │ +   Satu atau lebih   \d+        │ │
│ │ |   OR (atau)        Bab|BAB     │ │
│ │ ...                               │ │
│ └───────────────────────────────────┘ │
│ ┌─ Escape Karakter Khusus ─────────┐ │
│ │ (   harus \(       ) harus \)    │ │
│ │ ...                               │ │
│ └───────────────────────────────────┘ │
│ ┌─ Regulasi Indonesia ─────────────┐ │
│ │ Bab   BAB\s+[IVXLCDM]+           │ │
│ │ Pasal Pasal\s+\d+                │ │
│ │ ...                               │ │
│ └───────────────────────────────────┘ │
│                                      │
│ [Bab  | BAB\s+[IVXLCDM]+ | T | X]  │
│ [Pasal| Pasal\s+\d+      | T | X]  │
│ [Ayat | \(\d+\)           | T | X]  │
└──────────────────────────────────────┘
```

---

## Daftar Tabel Referensi

### 1. Karakter Umum

| Simbol | Nama | Fungsi | Contoh |
|---|---|---|---|
| `\s` | Spasi putih | Cocokkan spasi, tab, newline | `Pasal\s+\d+` → "Pasal 5" |
| `\S` | Bukan spasi | Kebalikan `\s` | `\S+` → "BAB" |
| `\d` | Digit | Cocokkan angka 0-9 | `\d{4}` → "2024" |
| `\D` | Bukan digit | Kebalikan `\d` | `\D+` → "Pasal" |
| `\w` | Word char | Huruf, angka, underscore | `\w+` → "BAB_1" |
| `\W` | Bukan word | Kebalikan `\w` | |
| `.` | Titik | Karakter apa saja (kecuali newline) | `Pasal.1` → "Pasal 1" |

### 2. Kuantifier

| Simbol | Nama | Fungsi | Contoh |
|---|---|---|---|
| `+` | Satu atau lebih | Minimal 1, bisa berulang | `\d+` → "123" |
| `*` | Nol atau lebih | Bisa tidak ada | `BAB\s*\d+` |
| `?` | Nol atau satu | Opsional | `Pasals?` → "Pasal"/"Pasals" |
| `{n}` | Tepat n kali | | `\d{4}` → "2024" |
| `{n,m}` | n sampai m kali | | `\d{1,3}` → "1" s/d "999" |
| `{n,}` | Minimal n kali | n atau lebih | `\d{2,}` → minimal 2 digit |

### 3. Logika & Grouping

| Simbol | Nama | Fungsi | Contoh |
|---|---|---|---|
| `\|` | OR (atau) | Cocokkan salah satu alternatif | `Bab\|BAB` → "Bab" atau "BAB" |
| `(…)` | Capture group | Tangkap bagian sebagai value metadata | `Pasal\s+(\d+)` → value: "5" |
| `(?:…)` | Non-capture group | Kelompokkan tanpa menangkap value | `(?:Bab\|BAB)\s+\d+` |
| `[abc]` | Character class | Salah satu karakter di dalam bracket | `[IVXLCDM]+` → "XIV" |
| `[a-z]` | Range | Rentang karakter dari a sampai z | `[a-z]` → huruf kecil |
| `[^abc]` | Negasi class | Bukan karakter yang disebut | `[^0-9]` → bukan angka |

### 4. Anchor & Boundary

| Simbol | Nama | Fungsi | Contoh |
|---|---|---|---|
| `^` | Awal baris | Harus di awal baris | `^BAB` → baris yang diawali "BAB" |
| `$` | Akhir baris | Harus di akhir baris | `\.$` → baris yang diakhiri titik |
| `\b` | Word boundary | Batas kata | `\bPasal\b` → bukan "Pasalnya" |

### 5. Escape Karakter Khusus

Karakter berikut memiliki arti khusus di regex. Untuk mencocokkan karakter literal-nya, tambahkan `\` di depannya.

| Karakter yang ditangkap | Penulisan di regex | Keterangan |
|---|---|---|
| Kurung buka `(` | `\(` | Tanpa escape = awal capture group |
| Kurung tutup `)` | `\)` | Tanpa escape = akhir capture group |
| Titik `.` | `\.` | Tanpa escape = karakter apa saja |
| Plus `+` | `\+` | Tanpa escape = kuantifier 1 atau lebih |
| Bintang `*` | `\*` | Tanpa escape = kuantifier 0 atau lebih |
| Tanda tanya `?` | `\?` | Tanpa escape = kuantifier opsional |
| Garis miring `\` | `\\` | Double backslash untuk literal |
| Pipe `|` | `\|` | Tanpa escape = OR operator |
| Kurung siku `[` | `\[` | Tanpa escape = awal character class |
| Kurung kurawal `{` | `\{` | Tanpa escape = awal kuantifier |
| Pangkat `^` | `\^` | Tanpa escape = anchor awal baris |
| Dollar `$` | `\$` | Tanpa escape = anchor akhir baris |

### 6. Contoh Pattern untuk Regulasi Indonesia

| Yang ingin ditangkap | Pattern | Contoh Match |
|---|---|---|
| Bab (Romawi) | `BAB\s+[IVXLCDM]+` | "BAB I", "BAB XII" |
| Pasal (angka) | `Pasal\s+\d+` | "Pasal 1", "Pasal 23" |
| Ayat (angka dalam kurung) | `\(\d+\)` | "(1)", "(2)", "(3)" |
| Huruf ayat | `\([a-z]\)` | "(a)", "(b)", "(c)" |
| Bab ATAU Pasal (OR) | `BAB\s+[IVXLCDM]+\|Pasal\s+\d+` | "BAB I" atau "Pasal 5" |
| Nomor Peraturan | `Nomor\s+\d+\s+Tahun\s+\d{4}` | "Nomor 12 Tahun 2024" |
| Undang-Undang | `UU\s*(?:No\.?\s*)?\d+\s*(?:Tahun\s*)?\d{4}` | "UU No. 12 Tahun 2024" |
| Tanggal | `\d{1,2}\s+\w+\s+\d{4}` | "1 Januari 2024" |
| Huruf dalam pasal | `huruf\s+[a-z]` | "huruf a", "huruf b" |
| Angka dengan titik (ayat) | `\d+\.\d+` | "1.1", "2.3" |

---

## Implementasi

1. Buat komponen baru `RegexReference.jsx` — berisi tabel referensi dengan toggle collapsible
2. Import dan taruh di `App.jsx` antara teks penjelasan dan daftar pattern rows
3. State toggle disimpan di dalam komponen (local state `useState`)
4. Styling: tabel kecil `text-[11px]`, header kategori bold, monospace untuk simbol/pattern
5. Setiap section bisa di-collapse/expand sendiri
