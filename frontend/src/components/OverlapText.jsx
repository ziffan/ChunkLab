export default function OverlapText({ text, overlapStartChars, overlapEndChars }) {
  const prefixEnd = overlapStartChars;
  const suffixStart = text.length - overlapEndChars;

  if (overlapStartChars === 0 && overlapEndChars === 0) {
    return <span>{text}</span>;
  }

  // If overlap spans entire text
  if (prefixEnd > suffixStart) {
    return (
      <span className="bg-amber-500/20 text-amber-300 rounded-sm px-0.5">{text}</span>
    );
  }

  return (
    <>
      {prefixEnd > 0 && (
        <span className="bg-amber-500/20 text-amber-300 rounded-sm px-0.5" title="Overlap with previous chunk">{text.slice(0, prefixEnd)}</span>
      )}
      <span>{text.slice(prefixEnd, suffixStart)}</span>
      {overlapEndChars > 0 && (
        <span className="bg-cyan-500/20 text-cyan-300 rounded-sm px-0.5" title="Overlap with next chunk">{text.slice(suffixStart)}</span>
      )}
    </>
  );
}
