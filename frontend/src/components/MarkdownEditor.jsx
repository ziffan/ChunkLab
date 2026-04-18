export default function MarkdownEditor({ value, onChange }) {
  return (
    <textarea
      className="w-full min-h-[200px] resize-y bg-slate-700 border border-slate-600 text-slate-100 rounded-lg p-3 font-mono text-[13px] focus:outline-none focus:border-indigo-500"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Paste your Markdown here..."
    />
  );
}
