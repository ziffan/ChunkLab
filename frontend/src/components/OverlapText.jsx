export default function OverlapText({ text, overlapStartChars, overlapEndChars }) {
  const prefixEnd = overlapStartChars;
  const suffixStart = text.length - overlapEndChars;

  if (overlapStartChars === 0 && overlapEndChars === 0) {
    return <span>{text}</span>;
  }

  if (prefixEnd > suffixStart) {
    return (
      <span className="bg-amber-100 text-amber-800">{text}</span>
    );
  }

  return (
    <>
      {prefixEnd > 0 && (
        <span className="bg-amber-100 text-amber-800">{text.slice(0, prefixEnd)}</span>
      )}
      <span>{text.slice(prefixEnd, suffixStart)}</span>
      {overlapEndChars > 0 && (
        <span className="bg-cyan-100 text-cyan-800">{text.slice(suffixStart)}</span>
      )}
    </>
  );
}
