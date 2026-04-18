import { useState, useEffect, useCallback } from 'react';

export default function ExportButton({ chunks, tokenCounts, isMock }) {
  const [status, setStatus] = useState('idle');

  useEffect(() => {
    if (status !== 'idle') {
      const timer = setTimeout(() => setStatus('idle'), 2000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const handleExport = useCallback(async () => {
    const exportArray = chunks.map((c, i) => ({
      index: c.index,
      text: c.text,
      char_count: c.char_count,
      overlap_start_chars: c.overlap_start_chars,
      overlap_end_chars: c.overlap_end_chars,
      metadata: c.metadata,
      token_count: tokenCounts[i] ?? null,
      is_mock_token: isMock,
    }));

    try {
      await navigator.clipboard.writeText(JSON.stringify(exportArray, null, 2));
      setStatus('copied');
    } catch {
      setStatus('error');
    }
  }, [chunks, tokenCounts, isMock]);

  const label = status === 'copied' ? 'Copied!' : status === 'error' ? 'Failed' : 'Export JSON';

  return (
    <button
      onClick={handleExport}
      disabled={chunks.length === 0}
      className="h-9 px-4 bg-indigo-500 hover:bg-indigo-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded text-[13px] font-medium"
    >
      {label}
    </button>
  );
}
