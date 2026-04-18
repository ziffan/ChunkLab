import { useEffect, useRef } from 'react';

export default function AboutModal({ open, onClose }) {
  const overlayRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <div className="bg-slate-800 border border-slate-600 rounded-xl max-w-lg w-full mx-4 shadow-2xl">
        <div className="flex items-center justify-between px-5 pt-4 pb-2 border-b border-slate-700">
          <h2 className="text-[16px] font-bold text-slate-100">Tentang Aplikasi</h2>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-[16px]"
          >
            ✕
          </button>
        </div>
        <div className="px-5 py-4 space-y-4 text-[13px] text-slate-300 leading-relaxed max-h-[70vh] overflow-y-auto">
          <div>
            <h3 className="text-[14px] font-bold text-slate-100 mb-1">ChunkLab</h3>
            <p>
              <em>The Interactive Regex & Chunking Sandbox</em> — alat interaktif berbasis browser untuk menguji dan memvalidasi konfigurasi pipeline <em>text chunking</em> sebelum mengekspor ke Vector Database. Membantu Anda membagi dokumen Markdown menjadi potongan-potongan (chunk) dengan ukuran dan overlap yang dapat diatur, mengekstrak metadata menggunakan regex, serta mengestimasi jumlah token per chunk agar tidak melebihi batas konteks model embedding.
            </p>
          </div>

          <div>
            <h3 className="text-[12px] uppercase text-slate-400 font-semibold mb-1">Fitur Utama</h3>
            <ul className="list-disc list-inside space-y-1 text-slate-300">
              <li>Sliding-window chunking dengan ukuran dan overlap yang dapat diatur</li>
              <li>Regex pattern untuk ekstraksi metadata otomatis (Bab, Pasal, Ayat, dll.)</li>
              <li>Estimasi token per chunk via berbagai provider (OpenAI, Gemini, Ollama, dll.)</li>
              <li>Visualisasi overlap antar chunk (highlight amber/cyan)</li>
              <li>Export hasil ke JSON untuk clipboard</li>
              <li>Parameter min/max token untuk memastikan chunk sesuai batas model</li>
            </ul>
          </div>

          <div>
            <h3 className="text-[12px] uppercase text-slate-400 font-semibold mb-1">Cara Pakai</h3>
            <ol className="list-decimal list-inside space-y-1 text-slate-300">
              <li>Paste teks Markdown di editor</li>
              <li>Atur Chunk Size, Overlap, dan batas token</li>
              <li>Tambahkan regex pattern untuk menangkap metadata</li>
              <li>Klik <em>Estimate Tokens</em> untuk cek token per chunk</li>
              <li>Klik <em>Export JSON</em> untuk menyalin hasil</li>
            </ol>
          </div>

          <div className="border-t border-slate-700 pt-3">
            <h3 className="text-[14px] font-bold text-slate-100 mb-1">Tentang Proyek</h3>
            <p>
              Aplikasi ini merupakan proyek open source yang saya kembangkan sebagai wujud hobi dan antusiasme terhadap teknologi. Di sela-sela kesibukan pekerjaan utama, saya mendedikasikan waktu luang untuk membangun alat yang bermanfaat sekaligus sebagai sarana untuk terus belajar secara mandiri.
            </p>
          </div>

          <div>
            <h3 className="text-[14px] font-bold text-slate-100 mb-1">Filosofi Proyek</h3>
            <ul className="space-y-2 text-slate-300">
              <li>
                <strong className="text-amber-400">Hobby-Driven:</strong> Fokus pada penyelesaian masalah nyata dan eksplorasi fitur secara kreatif di waktu luang.
              </li>
              <li>
                <strong className="text-amber-400">Hybrid Development:</strong> Dalam prosesnya, saya bereksperimen menggunakan bantuan AI Coding Agents (seperti Gemini CLI, Claude Code, Qwen Code, dan Opencode) untuk mempercepat iterasi dan memahami logika pemrograman yang lebih kompleks.
              </li>
              <li>
                <strong className="text-amber-400">Belajar Bersama:</strong> Sebagai pemula, saya membuka kode ini agar kita bisa saling berbagi ilmu. Saya sangat terbuka terhadap koreksi atas hasil kode yang dibantu oleh AI maupun kode yang saya tulis manual.
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-[14px] font-bold text-slate-100 mb-1">Pengembangan & Kolaborasi</h3>
            <p className="mb-2">
              Saya menyadari bahwa aplikasi ini masih dalam tahap pengembangan dan jauh dari sempurna. Masukan, kritik, maupun saran arsitektur dari Anda sangat saya harapkan untuk membantu saya berkembang.
            </p>
            <div className="space-y-1 text-[12px]">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">GitHub:</span>
                <a href="https://github.com/ziffan" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">github.com/ziffan</a>
              </div>
              <p className="text-slate-400">
                Jika Anda menemukan bug atau memiliki saran optimasi, jangan ragu untuk berinteraksi melalui Issue atau kirimkan Pull Request.
              </p>
            </div>
          </div>

          <div>
            <h3 className="text-[14px] font-bold text-slate-100 mb-1">Dukung Perjalanan Saya</h3>
            <p className="mb-2">
              Setiap dukungan adalah bahan bakar bagi saya untuk tetap konsisten belajar dan merilis proyek-proyek bermanfaat lainnya. Jika aplikasi ini membantu Anda, pertimbangkan untuk memberikan apresiasi melalui:
            </p>
            <div className="space-y-1 text-[12px]">
              <div className="flex items-center gap-2">
                <span className="text-slate-400 w-28">Saweria (Lokal)</span>
                <a href="https://saweria.co/kampusmerahdeveloper" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">saweria.co/kampusmerahdeveloper</a>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 w-28">Ko-fi (Global)</span>
                <a href="https://ko-fi.com/kampusmerahdev" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">ko-fi.com/kampusmerahdev</a>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 w-28">Patreon</span>
                <a href="https://patreon.com/c/Ziffan" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">patreon.com/c/Ziffan</a>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-700 pt-3">
            <h3 className="text-[14px] font-bold text-slate-100 mb-1">Mengenai Pengembang</h3>
            <p>
              Proyek ini dikembangkan secara personal oleh <strong className="text-slate-100">Ziffany Firdinal</strong> (<a href="https://github.com/ziffan" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">@ziffan</a>).
            </p>
            <p className="mt-1 text-slate-400 italic">
              Seorang pembelajar yang mencoba memberi manfaat melalui kolaborasi antara kreativitas manusia dan bantuan AI.
            </p>
          </div>

          <div className="text-slate-500 text-[11px] pt-2 border-t border-slate-700">
            Versi 1.0.0 — FastAPI + React 18 + Tailwind CSS
          </div>
        </div>
      </div>
    </div>
  );
}
