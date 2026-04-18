export default function RegexPatternRow({ pattern, onLabelChange, onPatternChange, onTest, onRemove }) {
  return (
    <div className="mb-2">
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={pattern.label}
          onChange={(e) => onLabelChange(pattern.id, e.target.value)}
          placeholder="Label"
          className="w-20 h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
        />
        <input
          type="text"
          value={pattern.pattern}
          onChange={(e) => onPatternChange(pattern.id, e.target.value)}
          placeholder="Regex pattern"
          className={`flex-1 h-9 bg-slate-700 border text-slate-100 rounded px-2 text-[13px] font-mono ${
            pattern.testError ? 'border-red-400' : 'border-slate-600'
          }`}
        />
        <button
          onClick={() => onTest(pattern.id)}
          className="h-9 px-3 bg-indigo-500 hover:bg-indigo-600 text-white rounded text-[13px]"
        >
          T
        </button>
        <button
          onClick={() => onRemove(pattern.id)}
          className="h-9 px-3 bg-slate-600 hover:bg-slate-500 text-white rounded text-[13px]"
        >
          X
        </button>
      </div>
      {pattern.testError && (
        <div className="text-red-400 text-[11px] mt-1">{pattern.testError}</div>
      )}
      {pattern.testResult && pattern.testResult.is_valid && (
        <div className="text-green-400 text-[11px] mt-1">
          ✓ {pattern.testResult.match_count} matches in document
        </div>
      )}
    </div>
  );
}
