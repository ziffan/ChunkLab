import { useState, useRef, useEffect } from 'react';
import { dump as yamlDump } from 'js-yaml';

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

function downloadFile(content, filename, mimeType = 'text/plain') {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function buildResultsJson(chunks, tokenCounts, isMock) {
  return chunks.map((c, i) => ({
    index: c.index,
    text: c.text,
    char_count: c.char_count,
    overlap_start_chars: c.overlap_start_chars,
    overlap_end_chars: c.overlap_end_chars,
    boundary_quality: c.boundary_quality,
    information_density: c.information_density,
    is_complete: c.is_complete,
    metadata: c.metadata,
    token_count: tokenCounts[i] ?? null,
    is_mock_token: isMock,
  }));
}

export default function ExportButton({
  chunks,
  tokenCounts,
  isMock,
  strategy = 'fixed',
  params = { chunk_size: 512, chunk_overlap: 50 },
  strategyParams = {},
  regexPatterns = [],
}) {
  const [open, setOpen] = useState(false);
  const [flash, setFlash] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (!ref.current?.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  useEffect(() => {
    if (!flash) return;
    const t = setTimeout(() => setFlash(null), 1800);
    return () => clearTimeout(t);
  }, [flash]);

  const ts = timestamp();

  const STRATEGY_DEFAULTS = {
    legal_id: {
      unit: 'pasal',
      max_chunk_chars: 1100,
      min_chunk_chars: 0,
      chunk_overlap: 0,
      include_parent_context: true,
    },
    sentence: { language: 'en', max_sentences_per_chunk: 5, chunk_overlap_sentences: 1 },
    sentence_id: { max_sentences_per_chunk: 5, chunk_overlap_sentences: 1 },
    markdown: { header_level: 2, include_parent_headers: true, max_chunk_chars: 4000 },
    token: { chunk_size: 512, chunk_overlap: 50 },
  };

  const exportConfig = () => {
    const defaults = STRATEGY_DEFAULTS[strategy] || {};
    const config = {
      exported_at: new Date().toISOString(),
      strategy,
      chunk_size: params.chunk_size,
      chunk_overlap: params.chunk_overlap,
      strategy_params: { ...defaults, ...strategyParams },
      regex_patterns: regexPatterns
        .filter((p) => p.label && p.pattern)
        .map((p) => ({ label: p.label, pattern: p.pattern })),
    };
    downloadFile(JSON.stringify(config, null, 2), `chunklab_config_${ts}.json`, 'application/json');
    setFlash('config');
    setOpen(false);
  };

  const exportResultsJson = () => {
    const data = buildResultsJson(chunks, tokenCounts, isMock);
    downloadFile(JSON.stringify(data, null, 2), `chunklab_export_${ts}.json`, 'application/json');
    setFlash('json');
    setOpen(false);
  };

  const exportResultsJsonl = () => {
    const lines = chunks
      .map((c, i) =>
        JSON.stringify({
          index: c.index,
          text: c.text,
          metadata: c.metadata,
          token_count: tokenCounts[i] ?? null,
        })
      )
      .join('\n');
    downloadFile(lines, `chunklab_export_${ts}.jsonl`, 'application/x-ndjson');
    setFlash('jsonl');
    setOpen(false);
  };

  const exportResultsYaml = () => {
    const data = buildResultsJson(chunks, tokenCounts, isMock);
    downloadFile(yamlDump(data), `chunklab_export_${ts}.yaml`, 'text/yaml');
    setFlash('yaml');
    setOpen(false);
  };

  const disabled = chunks.length === 0;

  return (
    <div ref={ref} className="relative flex gap-2">
      <button
        onClick={exportConfig}
        disabled={disabled}
        className="h-9 px-4 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 rounded text-[13px]"
      >
        {flash === 'config' ? 'Saved!' : 'Export Config'}
      </button>

      <div className="relative">
        <button
          onClick={() => setOpen((v) => !v)}
          disabled={disabled}
          className="h-9 px-4 bg-indigo-500 hover:bg-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded text-[13px] font-medium"
        >
          {flash && flash !== 'config' ? 'Saved!' : 'Export Results ▾'}
        </button>

        {open && (
          <div className="absolute right-0 top-10 z-50 bg-slate-800 border border-slate-600 rounded-lg shadow-lg py-1 min-w-[140px]">
            {[
              { label: 'JSON', action: exportResultsJson },
              { label: 'JSONL', action: exportResultsJsonl },
              { label: 'YAML', action: exportResultsYaml },
            ].map(({ label, action }) => (
              <button
                key={label}
                onClick={action}
                className="w-full text-left px-4 py-2 text-[13px] text-slate-200 hover:bg-slate-700"
              >
                {label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
