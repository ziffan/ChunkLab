export default function ChunkLegend() {
  return (
    <div className="flex items-center gap-x-3 gap-y-1 mb-3 px-2.5 py-1.5 bg-slate-800 border border-slate-700 rounded text-[11px] text-slate-400 flex-wrap">
      <span className="text-slate-500 font-semibold uppercase tracking-wide text-[10px] shrink-0">Legenda</span>

      <span className="flex items-center gap-1.5 shrink-0">
        <span className="flex gap-0.5 items-center">
          <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
          <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
          <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
        </span>
        <strong className="text-slate-300">BQ</strong>
        <span>Boundary Quality —</span>
        <span className="text-emerald-400">100%</span> kedua ujung di batas kalimat ·
        <span className="text-amber-400">50%</span> satu ujung ·
        <span className="text-red-400">0%</span> keduanya terpotong
      </span>

      <span className="text-slate-600">|</span>

      <span className="flex items-center gap-1 shrink-0">
        <strong className="text-slate-300">ID</strong>
        <span>Information Density — rasio karakter non-spasi; rendah berarti banyak baris kosong</span>
      </span>

      <span className="text-slate-600">|</span>

      <span className="flex items-center gap-1 shrink-0">
        <span className="text-amber-400 font-medium">⚠ trun</span>
        <span>— chunk terpotong di tengah kata</span>
      </span>
    </div>
  );
}
