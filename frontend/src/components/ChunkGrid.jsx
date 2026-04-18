import ChunkCard from './ChunkCard';

export default function ChunkGrid({ chunks, tokenCounts, isMock, isTokenizing, contextLimit, minTokens, maxTokens, isLoading, error }) {
  if (isLoading) {
    return (
      <div>
        {[0, 1, 2].map((i) => (
          <div key={i} className="bg-slate-700 rounded-lg p-3 mb-2 animate-pulse h-24" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-300 text-red-600 rounded-lg p-3 text-sm">
        {error.message}
      </div>
    );
  }

  if (chunks.length === 0) {
    return (
      <div className="text-slate-400 text-center py-12">
        Paste Markdown above to begin
      </div>
    );
  }

  return (
    <div className="overflow-y-auto max-h-[calc(100vh-120px)]">
      {chunks.map((chunk, i) => (
        <ChunkCard
          key={chunk.index}
          chunk={chunk}
          tokenCount={tokenCounts[i] ?? null}
          isMock={isMock}
          isTokenizing={isTokenizing}
          contextLimit={contextLimit}
          minTokens={minTokens}
          maxTokens={maxTokens}
        />
      ))}
    </div>
  );
}
