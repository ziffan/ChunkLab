import OverlapText from './OverlapText';
import MetadataBadge from './MetadataBadge';
import TokenBadge from './TokenBadge';
import QualityBadge from './QualityBadge';

function MdBreadcrumb({ value }) {
  const parts = value.split(' > ');
  return (
    <div className="flex items-center gap-1 flex-wrap mb-1.5 text-[10px] text-slate-400">
      {parts.map((part, i) => (
        <span key={i} className="flex items-center gap-1">
          <span>{part}</span>
          {i < parts.length - 1 && <span className="text-slate-600">›</span>}
        </span>
      ))}
    </div>
  );
}

export default function ChunkCard({ chunk, tokenCount, isMock, isTokenizing, contextLimit, minTokens, maxTokens }) {
  const mdPath = chunk.metadata?.find((m) => m.pattern_id === '_md_path');
  const userMetadata = chunk.metadata?.filter((m) => m.pattern_id !== '_md_path') ?? [];

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 mb-2 font-mono text-[13px]">
      {mdPath && <MdBreadcrumb value={mdPath.value} />}
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-200 font-semibold">
          Chunk #{chunk.index + 1}
        </span>
        <TokenBadge
          tokenCount={tokenCount}
          contextLimit={contextLimit}
          minTokens={minTokens}
          maxTokens={maxTokens}
          isMock={isMock}
          isLoading={isTokenizing}
        />
      </div>
      <div className="text-slate-100 whitespace-pre-wrap break-all mb-2">
        <OverlapText
          text={chunk.text}
          overlapStartChars={chunk.overlap_start_chars}
          overlapEndChars={chunk.overlap_end_chars}
        />
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-slate-400 text-[12px]">
          {chunk.char_count} chars
        </span>
        {chunk.boundary_quality != null && (
          <QualityBadge
            boundaryQuality={chunk.boundary_quality}
            informationDensity={chunk.information_density}
            isComplete={chunk.is_complete}
          />
        )}
        {userMetadata.map((m, i) => (
          <MetadataBadge
            key={`${m.pattern_id}-${i}`}
            label={m.label}
            value={m.value}
            colorIndex={i}
          />
        ))}
      </div>
    </div>
  );
}
