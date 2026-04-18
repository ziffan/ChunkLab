const TOKEN_COLORS = {
  green: 'bg-green-100 text-green-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  orange: 'bg-orange-100 text-orange-800',
  red: 'bg-red-100 text-red-800',
  blue: 'bg-blue-100 text-blue-800',
  gray: 'bg-gray-100 text-gray-600',
};

export default function TokenBadge({ tokenCount, contextLimit, minTokens, maxTokens, isMock, isLoading }) {
  if (isLoading) {
    return (
      <span className={`inline-block px-2 rounded-full text-[11px] ${TOKEN_COLORS.gray}`}>
        ...
      </span>
    );
  }

  if (tokenCount === null || tokenCount === undefined) {
    return (
      <span className={`inline-block px-2 rounded-full text-[11px] ${TOKEN_COLORS.gray}`}>
        —
      </span>
    );
  }

  if (isMock) {
    const belowMin = minTokens != null && tokenCount < minTokens;
    const aboveMax = maxTokens != null && tokenCount > maxTokens;
    let colorKey = 'gray';
    if (aboveMax) colorKey = 'red';
    else if (belowMin) colorKey = 'blue';
    return (
      <span className={`inline-block px-2 rounded-full text-[11px] ${TOKEN_COLORS[colorKey]}`}>
        ~{tokenCount.toLocaleString()} <span className="text-[9px]">MOCK</span>
        {belowMin && <span className="text-[9px] ml-1">MIN</span>}
        {aboveMax && <span className="text-[9px] ml-1">MAX</span>}
      </span>
    );
  }

  const aboveMax = maxTokens != null && tokenCount > maxTokens;
  const belowMin = minTokens != null && tokenCount < minTokens;

  let colorKey = 'green';
  if (aboveMax) colorKey = 'red';
  else if (contextLimit != null && tokenCount / contextLimit >= 1.0) colorKey = 'red';
  else if (contextLimit != null && tokenCount / contextLimit >= 0.9) colorKey = 'orange';
  else if (contextLimit != null && tokenCount / contextLimit >= 0.7) colorKey = 'yellow';
  else if (belowMin) colorKey = 'blue';

  return (
    <span className={`inline-block px-2 rounded-full text-[11px] ${TOKEN_COLORS[colorKey]}`}>
      {tokenCount.toLocaleString()}
      {belowMin && <span className="text-[9px] ml-1">MIN</span>}
      {aboveMax && <span className="text-[9px] ml-1">MAX</span>}
    </span>
  );
}
