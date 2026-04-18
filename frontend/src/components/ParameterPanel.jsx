export default function ParameterPanel({
  chunkSize,
  chunkOverlap,
  minTokens,
  maxTokens,
  onChunkSizeChange,
  onChunkOverlapChange,
  onMinTokensChange,
  onMaxTokensChange,
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-[12px] uppercase text-slate-400 mb-1">Chunk Size</label>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={50}
            max={8192}
            value={chunkSize}
            onChange={(e) => onChunkSizeChange(Number(e.target.value))}
            className="flex-1"
          />
          <input
            type="number"
            min={50}
            max={8192}
            value={chunkSize}
            onChange={(e) => onChunkSizeChange(Number(e.target.value))}
            onBlur={(e) => {
              const v = Number(e.target.value);
              onChunkSizeChange(Math.min(8192, Math.max(50, v)));
            }}
            className="w-20 h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
          />
        </div>
      </div>
      <div>
        <label className="block text-[12px] uppercase text-slate-400 mb-1">Overlap</label>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={0}
            max={chunkSize - 1}
            value={chunkOverlap}
            onChange={(e) => onChunkOverlapChange(Number(e.target.value))}
            className="flex-1"
          />
          <input
            type="number"
            min={0}
            max={chunkSize - 1}
            value={chunkOverlap}
            onChange={(e) => onChunkOverlapChange(Number(e.target.value))}
            onBlur={(e) => {
              const v = Number(e.target.value);
              onChunkOverlapChange(Math.min(chunkSize - 1, Math.max(0, v)));
            }}
            className="w-20 h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
          />
        </div>
      </div>
      <div>
        <label className="block text-[12px] uppercase text-slate-400 mb-1">Min Tokens</label>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={1}
            max={maxTokens - 1}
            value={minTokens}
            onChange={(e) => onMinTokensChange(Number(e.target.value))}
            className="flex-1"
          />
          <input
            type="number"
            min={1}
            max={maxTokens - 1}
            value={minTokens}
            onChange={(e) => onMinTokensChange(Number(e.target.value))}
            onBlur={(e) => {
              const v = Number(e.target.value);
              onMinTokensChange(Math.min(maxTokens - 1, Math.max(1, v)));
            }}
            className="w-20 h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
          />
        </div>
        <p className="text-[10px] text-slate-500 mt-1">Jumlah token minimum per chunk. Chunk di bawah batas ini ditandai warning.</p>
      </div>
      <div>
        <label className="block text-[12px] uppercase text-slate-400 mb-1">Max Tokens</label>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={minTokens + 1}
            max={8192}
            value={maxTokens}
            onChange={(e) => onMaxTokensChange(Number(e.target.value))}
            className="flex-1"
          />
          <input
            type="number"
            min={minTokens + 1}
            max={8192}
            value={maxTokens}
            onChange={(e) => onMaxTokensChange(Number(e.target.value))}
            onBlur={(e) => {
              const v = Number(e.target.value);
              onMaxTokensChange(Math.min(8192, Math.max(minTokens + 1, v)));
            }}
            className="w-20 h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
          />
        </div>
        <p className="text-[10px] text-slate-500 mt-1">Batas token maksimum. Chunk melebihi batas ini ditandai merah.</p>
      </div>
    </div>
  );
}
