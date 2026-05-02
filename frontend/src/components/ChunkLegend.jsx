export default function ChunkLegend() {
  return (
    <div className="mb-3 px-2.5 py-2 bg-slate-800 border border-slate-700 rounded text-[11px] text-slate-400 space-y-1.5">
      <span className="text-slate-500 font-semibold uppercase tracking-wide text-[10px]">Legenda</span>

      {/* Quality metrics */}
      <div className="flex items-center gap-x-3 flex-wrap gap-y-1">
        <span className="flex items-center gap-1.5">
          <span className="flex gap-0.5 items-center">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
            <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
            <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
          </span>
          <strong className="text-slate-300">BQ</strong>
          <span>Boundary Quality —</span>
          <span className="text-emerald-400">100%</span><span>kedua ujung di batas kalimat</span>
          <span className="text-slate-600">·</span>
          <span className="text-amber-400">50%</span><span>satu ujung</span>
          <span className="text-slate-600">·</span>
          <span className="text-red-400">0%</span><span>keduanya terpotong</span>
        </span>
        <span className="text-slate-600">|</span>
        <span className="flex items-center gap-1">
          <strong className="text-slate-300">ID</strong>
          <span>Information Density — rasio karakter non-spasi; rendah = banyak baris kosong</span>
        </span>
        <span className="text-slate-600">|</span>
        <span className="flex items-center gap-1">
          <span className="text-amber-400 font-medium">⚠ trun</span>
          <span>— terpotong di tengah kata</span>
        </span>
      </div>

      {/* Overlap */}
      <div className="flex items-center gap-x-3 flex-wrap gap-y-1">
        <span className="text-slate-500 text-[10px] uppercase tracking-wide shrink-0">Overlap</span>
        <span className="flex items-center gap-1">
          <span className="bg-amber-500/20 text-amber-300 rounded-sm px-1">teks</span>
          <span>— diwarisi dari chunk sebelumnya</span>
        </span>
        <span className="text-slate-600">|</span>
        <span className="flex items-center gap-1">
          <span className="bg-cyan-500/20 text-cyan-300 rounded-sm px-1">teks</span>
          <span>— akan diwariskan ke chunk berikutnya</span>
        </span>
      </div>

      {/* Token badge */}
      <div className="flex items-center gap-x-3 flex-wrap gap-y-1">
        <span className="text-slate-500 text-[10px] uppercase tracking-wide shrink-0">Token</span>
        <span className="flex items-center gap-1">
          <span className="bg-green-100 text-green-800 rounded-full px-1.5">N</span>
          <span>normal</span>
        </span>
        <span className="text-slate-600">·</span>
        <span className="flex items-center gap-1">
          <span className="bg-yellow-100 text-yellow-800 rounded-full px-1.5">N</span>
          <span>70–90% context limit</span>
        </span>
        <span className="text-slate-600">·</span>
        <span className="flex items-center gap-1">
          <span className="bg-orange-100 text-orange-800 rounded-full px-1.5">N</span>
          <span>90–100% context limit</span>
        </span>
        <span className="text-slate-600">·</span>
        <span className="flex items-center gap-1">
          <span className="bg-red-100 text-red-800 rounded-full px-1.5">N</span>
          <span>melebihi limit atau maxTokens</span>
        </span>
        <span className="text-slate-600">·</span>
        <span className="flex items-center gap-1">
          <span className="bg-blue-100 text-blue-800 rounded-full px-1.5">N</span>
          <span>di bawah minTokens</span>
        </span>
        <span className="text-slate-600">·</span>
        <span className="flex items-center gap-1">
          <span className="bg-gray-100 text-gray-600 rounded-full px-1.5">~N <span className="text-[9px]">MOCK</span></span>
          <span>estimasi char/4 (belum di-estimate)</span>
        </span>
      </div>
    </div>
  );
}
