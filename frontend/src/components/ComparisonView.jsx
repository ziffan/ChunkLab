import { useState } from 'react';
import { useComparison, defaultConfig } from '../hooks/useComparison';
import StrategySelector from './StrategySelector';
import ParameterPanel from './ParameterPanel';
import ChunkGrid from './ChunkGrid';
import DiffStats from './DiffStats';

function ConfigPane({ label, color, config, onChange, chunks, isLoading }) {
  const set = (patch) => onChange((prev) => ({ ...prev, ...patch }));

  return (
    <div className="flex flex-col gap-3 min-w-0">
      <div className={`flex items-center gap-2 pb-1 border-b ${color.border}`}>
        <span className={`text-[11px] font-bold uppercase tracking-widest ${color.text}`}>
          Config {label}
        </span>
        <span className="text-slate-500 text-[11px]">{chunks.length} chunks</span>
      </div>

      <StrategySelector
        strategy={config.strategy}
        strategyParams={config.strategyParams}
        onStrategyChange={(s) => set({ strategy: s })}
        onStrategyParamsChange={(sp) => set({ strategyParams: sp })}
      />

      <ParameterPanel
        strategy={config.strategy}
        chunkSize={config.chunk_size}
        chunkOverlap={config.chunk_overlap}
        minTokens={50}
        maxTokens={512}
        onChunkSizeChange={(v) =>
          set({ chunk_size: v, chunk_overlap: Math.min(config.chunk_overlap, v - 1) })
        }
        onChunkOverlapChange={(v) => set({ chunk_overlap: v })}
        onMinTokensChange={() => {}}
        onMaxTokensChange={() => {}}
      />

      <div className="overflow-y-auto max-h-[60vh]">
        <ChunkGrid
          chunks={chunks}
          tokenCounts={[]}
          isMock={false}
          isTokenizing={false}
          contextLimit={9999}
          minTokens={50}
          maxTokens={512}
          isLoading={isLoading}
          error={null}
        />
      </div>
    </div>
  );
}

const PANE_A = { border: 'border-indigo-700', text: 'text-indigo-400' };
const PANE_B = { border: 'border-amber-700', text: 'text-amber-400' };

export default function ComparisonView({ markdown, regexPatterns }) {
  const [configA, setConfigA] = useState(() => defaultConfig());
  const [configB, setConfigB] = useState(() =>
    defaultConfig({ strategy: 'recursive' })
  );

  const { chunksA, isLoadingA, chunksB, isLoadingB } = useComparison(
    markdown,
    configA,
    configB,
    regexPatterns
  );

  return (
    <div>
      <div className="grid grid-cols-2 gap-4">
        <ConfigPane
          label="A"
          color={PANE_A}
          config={configA}
          onChange={setConfigA}
          chunks={chunksA}
          isLoading={isLoadingA}
        />
        <ConfigPane
          label="B"
          color={PANE_B}
          config={configB}
          onChange={setConfigB}
          chunks={chunksB}
          isLoading={isLoadingB}
        />
      </div>
      <DiffStats chunksA={chunksA} chunksB={chunksB} />
    </div>
  );
}
