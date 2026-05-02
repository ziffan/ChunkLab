import { useRetrieval } from '../hooks/useRetrieval';

export default function RetrievalPanel({ chunks }) {
  const { query, setQuery, topK, setTopK, results, isLoading, error, isUnavailable, retrieve, clearResults } =
    useRetrieval();

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') retrieve(chunks);
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Query to find relevant chunks…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-3 text-[13px] placeholder:text-slate-500"
        />
        <select
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="h-9 bg-slate-700 border border-slate-600 text-slate-300 rounded px-2 text-[13px]"
        >
          {[5, 10, 25, 50].map((n) => (
            <option key={n} value={n}>Top {n}</option>
          ))}
        </select>
        <button
          onClick={() => retrieve(chunks)}
          disabled={isLoading || !query.trim() || !chunks.length}
          className="h-9 px-4 bg-indigo-500 hover:bg-indigo-600 disabled:opacity-40 text-white rounded text-[13px]"
        >
          {isLoading ? '…' : 'Retrieve'}
        </button>
        {results.length > 0 && (
          <button
            onClick={clearResults}
            className="h-9 px-3 bg-slate-700 hover:bg-slate-600 text-slate-400 rounded text-[12px]"
          >
            ✕
          </button>
        )}
      </div>

      {!chunks.length && (
        <p className="text-[11px] text-slate-500">Paste or upload text to enable retrieval.</p>
      )}

      {isUnavailable && (
        <div className="text-[11px] text-amber-400 bg-amber-500/10 border border-amber-500/30 rounded px-3 py-2">
          Retrieval unavailable — install extras:{' '}
          <code className="text-amber-300">pip install -r requirements-retrieval.txt</code>
        </div>
      )}

      {error && <p className="text-[11px] text-red-400">{error}</p>}

      {results.length > 0 && (
        <div className="space-y-2">
          {results.map((r) => (
            <div
              key={r.index}
              className="bg-slate-700 border border-slate-600 rounded p-2.5"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[12px] text-slate-300 font-medium">
                  Chunk #{r.index + 1}
                </span>
                <span className="text-[11px] text-indigo-300 font-mono">
                  {(r.score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="h-1 bg-slate-600 rounded mb-2 overflow-hidden">
                <div
                  className="h-1 bg-indigo-500 rounded"
                  style={{ width: `${Math.max(0, r.score * 100).toFixed(1)}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-400 line-clamp-2 font-mono">{r.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
