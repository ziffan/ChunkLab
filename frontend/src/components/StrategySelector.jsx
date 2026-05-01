const STRATEGIES = [
  { id: 'fixed',       label: 'Fixed Size' },
  { id: 'recursive',   label: 'Recursive Character' },
  { id: 'token',       label: 'Token Aware' },
  { id: 'sentence',    label: 'Sentence (pysbd)' },
  { id: 'sentence_id', label: 'Sentence — Indonesian (sentence_id)' },
  { id: 'markdown',    label: 'Markdown Structure' },
  { id: 'legal_id',    label: 'Legal Structure — Indonesian (legal_id)' },
];

const inputCls =
  'w-full h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]';

function Field({ label, hint, children }) {
  return (
    <div>
      <label className="block text-[12px] uppercase text-slate-400 mb-1">{label}</label>
      {children}
      {hint && <p className="text-[10px] text-slate-500 mt-1">{hint}</p>}
    </div>
  );
}

export default function StrategySelector({ strategy, strategyParams, onStrategyChange, onStrategyParamsChange }) {
  const set = (key, val) => onStrategyParamsChange({ ...strategyParams, [key]: val });

  return (
    <div className="space-y-3">
      <Field label="Strategy">
        <select
          value={strategy}
          onChange={(e) => onStrategyChange(e.target.value)}
          className={inputCls}
        >
          {STRATEGIES.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label}
            </option>
          ))}
        </select>
      </Field>

      {strategy === 'recursive' && (
        <Field
          label="Separators (one per line, optional)"
          hint="Leave empty to use defaults: \n\n → \n → '. ' → ' ' → char"
        >
          <textarea
            rows={3}
            placeholder={'\n\n\n\n. \n '}
            value={(strategyParams.separators ?? []).join('\n')}
            onChange={(e) => {
              const raw = e.target.value;
              set('separators', raw === '' ? undefined : raw.split('\n'));
            }}
            className="w-full bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 py-1.5 text-[12px] font-mono resize-none"
          />
        </Field>
      )}

      {strategy === 'token' && (
        <>
          <Field label="Chunk Size (tokens)">
            <input
              type="number"
              min={1}
              max={8192}
              value={strategyParams.chunk_size_tokens ?? 256}
              onChange={(e) => set('chunk_size_tokens', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
          <Field label="Overlap (tokens)">
            <input
              type="number"
              min={0}
              value={strategyParams.chunk_overlap_tokens ?? 20}
              onChange={(e) => set('chunk_overlap_tokens', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
          <Field label="Encoding">
            <select
              value={strategyParams.encoding_name ?? 'cl100k_base'}
              onChange={(e) => set('encoding_name', e.target.value)}
              className={inputCls}
            >
              <option value="cl100k_base">cl100k_base (GPT-4 / 3.5)</option>
              <option value="p50k_base">p50k_base (GPT-3)</option>
              <option value="o200k_base">o200k_base (GPT-4o)</option>
            </select>
          </Field>
        </>
      )}

      {strategy === 'sentence' && (
        <>
          <Field label="Language" hint="pysbd strategy — use sentence_id for Indonesian">
            <select
              value={strategyParams.language ?? 'en'}
              onChange={(e) => set('language', e.target.value)}
              className={inputCls}
            >
              <option value="am">Amharic (am)</option>
              <option value="ar">Arabic (ar)</option>
              <option value="hy">Armenian (hy)</option>
              <option value="bg">Bulgarian (bg)</option>
              <option value="my">Burmese (my)</option>
              <option value="zh">Chinese (zh)</option>
              <option value="da">Danish (da)</option>
              <option value="nl">Dutch (nl)</option>
              <option value="en">English (en)</option>
              <option value="fa">Farsi (fa)</option>
              <option value="fr">French (fr)</option>
              <option value="de">German (de)</option>
              <option value="el">Greek (el)</option>
              <option value="hi">Hindi (hi)</option>
              <option value="it">Italian (it)</option>
              <option value="ja">Japanese (ja)</option>
              <option value="kk">Kazakh (kk)</option>
              <option value="mr">Marathi (mr)</option>
              <option value="pl">Polish (pl)</option>
              <option value="ru">Russian (ru)</option>
              <option value="sk">Slovak (sk)</option>
              <option value="es">Spanish (es)</option>
              <option value="ur">Urdu (ur)</option>
            </select>
          </Field>
          <Field label="Sentences per Chunk">
            <input
              type="number"
              min={1}
              value={strategyParams.max_sentences_per_chunk ?? 5}
              onChange={(e) => set('max_sentences_per_chunk', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
          <Field label="Overlap (sentences)">
            <input
              type="number"
              min={0}
              value={strategyParams.chunk_overlap_sentences ?? 1}
              onChange={(e) => set('chunk_overlap_sentences', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
        </>
      )}

      {strategy === 'sentence_id' && (
        <>
          <Field label="Sentences per Chunk">
            <input
              type="number"
              min={1}
              value={strategyParams.max_sentences_per_chunk ?? 5}
              onChange={(e) => set('max_sentences_per_chunk', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
          <Field label="Overlap (sentences)">
            <input
              type="number"
              min={0}
              value={strategyParams.overlap_sentences ?? 1}
              onChange={(e) => set('overlap_sentences', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
          <Field label="Min Chunk Chars" hint="Chunks shorter than this are merged with the next">
            <input
              type="number"
              min={0}
              value={strategyParams.min_chunk_chars ?? 100}
              onChange={(e) => set('min_chunk_chars', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
        </>
      )}

      {strategy === 'legal_id' && (
        <>
          <Field label="Unit" hint="pasal: split at each Pasal. bab: split at each BAB. auto: chooses based on document size">
            <select
              value={strategyParams.unit ?? 'pasal'}
              onChange={(e) => set('unit', e.target.value)}
              className={inputCls}
            >
              <option value="pasal">Pasal</option>
              <option value="bab">BAB</option>
              <option value="auto">Auto</option>
            </select>
          </Field>
          <Field label="Max Chunk Chars" hint="Oversized Pasal blocks are sub-split by RecursiveCharacterChunker">
            <input
              type="number"
              min={500}
              value={strategyParams.max_chunk_chars ?? 4000}
              onChange={(e) => set('max_chunk_chars', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
          <Field label="Include Parent Context" hint="Prepends [BAB I > Pasal N] breadcrumb to each chunk">
            <select
              value={strategyParams.include_parent_context ?? true}
              onChange={(e) => set('include_parent_context', e.target.value === 'true')}
              className={inputCls}
            >
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </Field>
        </>
      )}

      {strategy === 'markdown' && (
        <>
          <Field label="Split at Header Level">
            <select
              value={strategyParams.header_level ?? 2}
              onChange={(e) => set('header_level', Number(e.target.value))}
              className={inputCls}
            >
              {[1, 2, 3, 4, 5, 6].map((l) => (
                <option key={l} value={l}>
                  H{l} and above
                </option>
              ))}
            </select>
          </Field>
          <Field label="Max Chunk Size (chars)">
            <input
              type="number"
              min={100}
              value={strategyParams.max_chunk_size ?? 2000}
              onChange={(e) => set('max_chunk_size', Number(e.target.value))}
              className={inputCls}
            />
          </Field>
        </>
      )}
    </div>
  );
}
