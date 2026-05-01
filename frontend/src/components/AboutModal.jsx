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
          <div className="flex justify-center mb-6">
            <img src="/logo.png" alt="ChunkLab Logo" className="h-24 w-auto" />
          </div>
          <div>
            <h3 className="text-[14px] font-bold text-slate-100 mb-1">ChunkLab</h3>
            <p>
              <em>The Interactive Regex & Chunking Sandbox</em> — alat interaktif berbasis browser untuk menguji dan memvalidasi konfigurasi pipeline <em>text chunking</em> sebelum mengekspor ke Vector Database. Mendukung berbagai strategi chunking, ekstraksi metadata via regex, estimasi token multi-provider, simulasi retrieval semantik, mode perbandingan dua konfigurasi, dan export ke berbagai format siap pakai.
            </p>
          </div>

          <div>
            <h3 className="text-[12px] uppercase text-slate-400 font-semibold mb-1">Fitur Utama</h3>
            <ul className="list-disc list-inside space-y-1 text-slate-300">
              <li><strong className="text-slate-200">7 strategi chunking</strong> — Fixed, Recursive, Token-aware (tiktoken), Sentence (pysbd), Sentence — Indonesian (sentence_id), Markdown Structure, Legal Structure — Indonesian (legal_id)</li>
              <li><strong className="text-slate-200">File upload</strong> — drag-and-drop atau klik untuk file <code className="bg-slate-700 px-1 rounded text-amber-300">.txt</code> / <code className="bg-slate-700 px-1 rounded text-amber-300">.md</code> hingga 500 KB</li>
              <li><strong className="text-slate-200">Quality metrics</strong> — Boundary Quality, Information Density, dan deteksi potongan tidak sempurna per chunk</li>
              <li><strong className="text-slate-200">Regex metadata</strong> — ekstraksi otomatis (Bab, Pasal, Ayat, dll.) dengan capture group</li>
              <li><strong className="text-slate-200">Markdown breadcrumb</strong> — jalur header (H1 › H2 › H3) otomatis ditampilkan per chunk</li>
              <li><strong className="text-slate-200">Retrieval simulation</strong> — query semantik top-K via sentence-transformers (opsional)</li>
              <li><strong className="text-slate-200">Comparison mode</strong> — bandingkan dua konfigurasi side-by-side dengan diff stats</li>
              <li><strong className="text-slate-200">Export multi-format</strong> — JSON, JSONL (siap Vector DB), YAML sebagai file download</li>
              <li><strong className="text-slate-200">API Spec</strong> — download OpenAPI spec langsung dari backend</li>
              <li><strong className="text-slate-200">Token estimation</strong> — multi-provider: OpenAI, Gemini, OpenRouter, Ollama, LM Studio</li>
            </ul>
          </div>

          <div>
            <h3 className="text-[12px] uppercase text-slate-400 font-semibold mb-1">Cara Pakai</h3>
            <ol className="list-decimal list-inside space-y-1 text-slate-300">
              <li>Paste teks Markdown di editor atau upload file .txt / .md</li>
              <li>Pilih strategi chunking dan atur parameter-nya</li>
              <li>Tambahkan regex pattern untuk menangkap metadata</li>
              <li>Lihat quality badge per chunk (BQ%, ID%, truncation warning)</li>
              <li>Gunakan <em>Compare</em> untuk membandingkan dua konfigurasi sekaligus</li>
              <li>Klik <em>Estimate Tokens</em> untuk cek token per chunk</li>
              <li>Export hasil via <em>Export Results</em> (JSON / JSONL / YAML)</li>
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
            Versi 2.1.0 — FastAPI + React 18 + Tailwind CSS
          </div>
        </div>
      </div>
    </div>
  );
}
