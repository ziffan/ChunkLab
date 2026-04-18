import { useState } from 'react';
import MarkdownEditor from './components/MarkdownEditor';
import ParameterPanel from './components/ParameterPanel';
import RegexPatternRow from './components/RegexPatternRow';
import RegexReference from './components/RegexReference';
import ResizablePanel from './components/ResizablePanel';
import ModelSelector from './components/ModelSelector';
import ChunkGrid from './components/ChunkGrid';
import ExportButton from './components/ExportButton';
import AboutModal from './components/AboutModal';
import { useChunker } from './hooks/useChunker';
import { useRegexPatterns } from './hooks/useRegexPatterns';
import { useTokenization } from './hooks/useTokenization';
import { PROVIDERS } from './constants/models';

const INITIAL_REGEX = [
  { id: crypto.randomUUID(), label: 'Bab', pattern: 'BAB\\s+[IVXLCDM]+', testResult: null, testError: null },
  { id: crypto.randomUUID(), label: 'Pasal', pattern: 'Pasal\\s+\\d+', testResult: null, testError: null },
  { id: crypto.randomUUID(), label: 'Ayat', pattern: '\\(\\d+\\)', testResult: null, testError: null },
];

export default function App() {
  const [markdown, setMarkdown] = useState('');
  const [params, setParams] = useState({ chunk_size: 512, chunk_overlap: 50 });
  const [minTokens, setMinTokens] = useState(50);
  const [maxTokens, setMaxTokens] = useState(512);
  const [aboutOpen, setAboutOpen] = useState(false);

  const {
    regexPatterns,
    cleanPatterns,
    handleAddPattern,
    handleRemovePattern,
    handleLabelChange,
    handlePatternChange,
    handleTestPattern,
  } = useRegexPatterns(INITIAL_REGEX, markdown);

  const {
    provider,
    setProvider,
    modelName,
    setModelName,
    tokenCounts,
    isTokenizing,
    tokenizeError,
    isMockToken,
    handleEstimateTokens,
  } = useTokenization();

  const contextLimit = PROVIDERS.find((p) => p.id === provider)?.contextLimit ?? 9999;

  const { chunks, isLoading, error } = useChunker(markdown, params, cleanPatterns);

  const totalChars = chunks.reduce((sum, c) => sum + c.char_count, 0);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h1 className="text-[18px] font-bold">ChunkLab <span className="text-[12px] font-normal text-slate-400 ml-1">The Interactive Regex & Chunking Sandbox</span></h1>
          <button
            onClick={() => setAboutOpen(true)}
            className="h-7 px-3 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-[12px]"
          >
            Tentang Aplikasi
          </button>
        </div>
        <ExportButton chunks={chunks} tokenCounts={tokenCounts} isMock={isMockToken} />
      </div>

      <div className="flex gap-4">
        <ResizablePanel direction="horizontal" defaultWidth={380} minW={200} className="max-h-[calc(100vh-80px)]">
          <div className="flex flex-col gap-2 flex-1 overflow-y-auto">
            <ResizablePanel title="Editor" defaultHeight={220} minH={100}>
              <MarkdownEditor value={markdown} onChange={setMarkdown} />
            </ResizablePanel>

            <ResizablePanel title="Parameters" defaultHeight={260} minH={80}>
              <ParameterPanel
                chunkSize={params.chunk_size}
                chunkOverlap={params.chunk_overlap}
                minTokens={minTokens}
                maxTokens={maxTokens}
                onChunkSizeChange={(v) => {
                  setParams((prev) => ({
                    chunk_size: v,
                    chunk_overlap: Math.min(prev.chunk_overlap, v - 1),
                  }));
                }}
                onChunkOverlapChange={(v) =>
                  setParams((prev) => ({ ...prev, chunk_overlap: v }))
                }
                onMinTokensChange={setMinTokens}
                onMaxTokensChange={setMaxTokens}
              />
            </ResizablePanel>

            <ResizablePanel title="Regex Patterns" defaultHeight={300} minH={100}>
              <div className="flex items-center justify-between mb-2">
                <div />
                <button
                  onClick={handleAddPattern}
                  className="h-7 px-3 bg-indigo-500 hover:bg-indigo-600 text-white rounded text-[12px]"
                >
                  +
                </button>
              </div>
              <div className="text-slate-400 text-[11px] mb-3 space-y-1">
                <p>Gunakan regex Python standar. <strong>Label</strong> adalah nama tag metadata, <strong>Pattern</strong> adalah ekspresi regex.</p>
                <p>Gunakan <code className="bg-slate-700 px-1 rounded text-amber-300">(grup)</code> untuk menangkap bagian tertentu. Contoh: <code className="bg-slate-700 px-1 rounded text-amber-300">Pasal\s+(\d+)</code> hanya menangkap angkanya.</p>
                <p>Tekan <span className="bg-indigo-500 px-1.5 py-0.5 rounded text-white text-[10px]">T</span> untuk menguji pola terhadap dokumen.</p>
              </div>
              <RegexReference />
              {regexPatterns.map((p) => (
                <RegexPatternRow
                  key={p.id}
                  pattern={p}
                  onLabelChange={handleLabelChange}
                  onPatternChange={handlePatternChange}
                  onTest={handleTestPattern}
                  onRemove={handleRemovePattern}
                />
              ))}
              {regexPatterns.length === 0 && (
                <div className="text-slate-500 text-[12px]">Tekan + untuk menambah pola regex baru.</div>
              )}
            </ResizablePanel>

            <ResizablePanel title="Model" defaultHeight={200} minH={80}>
              <ModelSelector
                provider={provider}
                modelName={modelName}
                onProviderChange={setProvider}
                onModelNameChange={setModelName}
                onEstimate={() => handleEstimateTokens(chunks)}
              />
            </ResizablePanel>
          </div>
        </ResizablePanel>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-4 mb-3">
            <span className="text-[13px] text-slate-400">
              Chunks: {chunks.length}
            </span>
            <span className="text-[13px] text-slate-400">
              Chars: {totalChars}
            </span>
          </div>
          {tokenizeError && (
            <div className="bg-red-50 border border-red-300 text-red-600 rounded-lg p-2 text-[12px] mb-3">
              {tokenizeError}
            </div>
          )}
          <ChunkGrid
            chunks={chunks}
            tokenCounts={tokenCounts}
            isMock={isMockToken}
            isTokenizing={isTokenizing}
            contextLimit={contextLimit}
            minTokens={minTokens}
            maxTokens={maxTokens}
            isLoading={isLoading}
            error={error}
          />
        </div>
      </div>
      <AboutModal open={aboutOpen} onClose={() => setAboutOpen(false)} />
    </div>
  );
}
