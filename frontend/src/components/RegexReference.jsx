import { useState } from 'react';

const SECTIONS = [
  {
    title: 'Karakter Umum',
    rows: [
      ['\\s', 'Spasi putih', 'Cocokkan spasi, tab, newline', 'Pasal\\s+\\d+ → "Pasal 5"'],
      ['\\S', 'Bukan spasi', 'Kebalikan \\s', '\\S+ → "BAB"'],
      ['\\d', 'Digit', 'Angka 0-9', '\\d{4} → "2024"'],
      ['\\D', 'Bukan digit', 'Kebalikan \\d', '\\D+ → "Pasal"'],
      ['\\w', 'Word char', 'Huruf, angka, underscore', '\\w+ → "BAB_1"'],
      ['\\W', 'Bukan word', 'Kebalikan \\w', ''],
      ['.', 'Titik', 'Karakter apa saja (kecuali newline)', 'Pasal.1 → "Pasal 1"'],
    ],
  },
  {
    title: 'Kuantifier',
    rows: [
      ['+', 'Satu atau lebih', 'Minimal 1, bisa berulang', '\\d+ → "123"'],
      ['*', 'Nol atau lebih', 'Bisa tidak ada', 'BAB\\s*\\d+'],
      ['?', 'Nol atau satu', 'Opsional', 'Pasals? → "Pasal"/"Pasals"'],
      ['{n}', 'Tepat n kali', '', '\\d{4} → "2024"'],
      ['{n,m}', 'n sampai m kali', '', '\\d{1,3} → "1" s/d "999"'],
      ['{n,}', 'Minimal n kali', 'n atau lebih', '\\d{2,} → min. 2 digit'],
    ],
  },
  {
    title: 'Logika & Grouping',
    rows: [
      ['|', 'OR (atau)', 'Cocokkan salah satu alternatif', 'Bab|BAB → "Bab" atau "BAB"'],
      ['(…)', 'Capture group', 'Tangkap bagian sebagai value', 'Pasal\\s+(\\d+) → value: "5"'],
      ['(?:…)', 'Non-capture', 'Kelompokkan tanpa menangkap', '(?:Bab|BAB)\\s+\\d+'],
      ['[abc]', 'Char class', 'Salah satu karakter di bracket', '[IVXLCDM]+ → "XIV"'],
      ['[a-z]', 'Range', 'Rentang karakter', '[a-z] → huruf kecil'],
      ['[^abc]', 'Negasi class', 'Bukan karakter tersebut', '[^0-9] → bukan angka'],
    ],
  },
  {
    title: 'Anchor & Boundary',
    rows: [
      ['^', 'Awal baris', 'Harus di awal baris', '^BAB → baris diawali "BAB"'],
      ['$', 'Akhir baris', 'Harus di akhir baris', '\\.$ → baris diakhiri titik'],
      ['\\b', 'Word boundary', 'Batas kata', '\\bPasal\\b → bukan "Pasalnya"'],
    ],
  },
  {
    title: 'Escape Karakter Khusus',
    rows: [
      ['\\(', 'Kurung buka (', 'Tanpa escape = awal capture group', '\\(\\d+\\) → "(1)"'],
      ['\\)', 'Kurung tutup )', 'Tanpa escape = akhir capture group', ''],
      ['\\.', 'Titik .', 'Tanpa escape = karakter apa saja', '\\d+\\.\\d+ → "1.1"'],
      ['\\+', 'Plus +', 'Tanpa escape = kuantifier 1+', ''],
      ['\\*', 'Bintang *', 'Tanpa escape = kuantifier 0+', ''],
      ['\\?', 'Tanda tanya ?', 'Tanpa escape = opsional', ''],
      ['\\\\', 'Backslash \\', 'Double backslash untuk literal', ''],
      ['\\|', 'Pipe |', 'Tanpa escape = OR operator', 'Bab\\|BAB → literal "|"'],
      ['\\[', 'Kurung siku [', 'Tanpa escape = character class', ''],
      ['\\{', 'Kurung kurawal {', 'Tanpa escape = kuantifier', ''],
      ['\\^', 'Pangkat ^', 'Tanpa escape = anchor awal', ''],
      ['\\$', 'Dollar $', 'Tanpa escape = anchor akhir', ''],
    ],
  },
  {
    title: 'Contoh: Regulasi Indonesia',
    headers: ['Yang ditangkap', 'Pattern', 'Contoh Match'],
    rows: [
      ['Bab (Romawi)', 'BAB\\s+[IVXLCDM]+', '"BAB I", "BAB XII"'],
      ['Pasal (angka)', 'Pasal\\s+\\d+', '"Pasal 1", "Pasal 23"'],
      ['Ayat (kurung)', '\\(\\d+\\)', '"(1)", "(2)", "(3)"'],
      ['Huruf ayat', '\\([a-z]\\)', '"(a)", "(b)", "(c)"'],
      ['Bab ATAU Pasal', 'BAB\\s+[IVXLCDM]+|Pasal\\s+\\d+', '"BAB I" atau "Pasal 5"'],
      ['Nomor Peraturan', 'Nomor\\s+\\d+\\s+Tahun\\s+\\d{4}', '"Nomor 12 Tahun 2024"'],
      ['Undang-Undang', 'UU\\s*(?:No\\.?\\s*)?\\d+\\s*(?:Tahun\\s*)?\\d{4}', '"UU No. 12 Tahun 2024"'],
      ['Tanggal', '\\d{1,2}\\s+\\w+\\s+\\d{4}', '"1 Januari 2024"'],
      ['Huruf dalam pasal', 'huruf\\s+[a-z]', '"huruf a", "huruf b"'],
      ['Angka dengan titik', '\\d+\\.\\d+', '"1.1", "2.3"'],
    ],
  },
];

function Section({ section }) {
  const [open, setOpen] = useState(false);
  const isIndo = !!section.headers;

  return (
    <div className="mb-1">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-1 text-[11px] font-semibold text-slate-300 hover:text-white py-1"
      >
        <span className={`transition-transform ${open ? 'rotate-90' : ''}`}>▶</span>
        {section.title}
      </button>
      {open && (
        <div className="overflow-x-auto">
          {isIndo ? (
            <table className="w-full text-[11px] border-collapse">
              <thead>
                <tr className="text-left text-slate-500">
                  <th className="pr-2 py-0.5 font-medium">{section.headers[0]}</th>
                  <th className="pr-2 py-0.5 font-medium">{section.headers[1]}</th>
                  <th className="py-0.5 font-medium">{section.headers[2]}</th>
                </tr>
              </thead>
              <tbody>
                {section.rows.map((r, i) => (
                  <tr key={i} className="border-t border-slate-700/50">
                    <td className="pr-2 py-0.5 text-slate-300">{r[0]}</td>
                    <td className="pr-2 py-0.5 font-mono text-amber-300">{r[1]}</td>
                    <td className="py-0.5 text-slate-400">{r[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-[11px] border-collapse">
              <thead>
                <tr className="text-left text-slate-500">
                  <th className="w-16 pr-2 py-0.5 font-medium">Simbol</th>
                  <th className="w-28 pr-2 py-0.5 font-medium">Nama</th>
                  <th className="pr-2 py-0.5 font-medium">Fungsi</th>
                  <th className="py-0.5 font-medium">Contoh</th>
                </tr>
              </thead>
              <tbody>
                {section.rows.map((r, i) => (
                  <tr key={i} className="border-t border-slate-700/50">
                    <td className="pr-2 py-0.5 font-mono text-amber-300">{r[0]}</td>
                    <td className="pr-2 py-0.5 text-slate-300">{r[1]}</td>
                    <td className="pr-2 py-0.5 text-slate-400">{r[2]}</td>
                    <td className="py-0.5 font-mono text-emerald-400">{r[3]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

export default function RegexReference() {
  const [open, setOpen] = useState(false);

  return (
    <div className="mb-3">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-[11px] font-semibold text-indigo-400 hover:text-indigo-300"
      >
        <span className={`transition-transform ${open ? 'rotate-90' : ''}`}>▶</span>
        Buka Referensi Regex
      </button>
      {open && (
        <div className="mt-2 bg-slate-900 border border-slate-700 rounded-lg p-2 max-h-[320px] overflow-y-auto">
          {SECTIONS.map((s) => (
            <Section key={s.title} section={s} />
          ))}
        </div>
      )}
    </div>
  );
}
