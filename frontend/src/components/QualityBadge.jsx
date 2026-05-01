function BoundaryDot({ score }) {
  const color =
    score >= 0.8
      ? 'bg-emerald-500'
      : score >= 0.5
      ? 'bg-amber-400'
      : 'bg-red-500';
  return (
    <span
      title={`Boundary quality: ${score.toFixed(2)}`}
      className={`inline-block w-2 h-2 rounded-full ${color}`}
    />
  );
}

export default function QualityBadge({ boundaryQuality, informationDensity, isComplete }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-slate-700 border border-slate-600 rounded text-[10px] text-slate-300">
      <BoundaryDot score={boundaryQuality} />
      <span title={`Boundary quality: ${boundaryQuality.toFixed(2)}`}>
        BQ {(boundaryQuality * 100).toFixed(0)}%
      </span>
      <span className="text-slate-500">·</span>
      <span title={`Information density: ${informationDensity.toFixed(4)}`}>
        ID {(informationDensity * 100).toFixed(0)}%
      </span>
      {!isComplete && (
        <>
          <span className="text-slate-500">·</span>
          <span className="text-amber-400" title="Chunk appears cut mid-word">⚠ trunc</span>
        </>
      )}
    </span>
  );
}
