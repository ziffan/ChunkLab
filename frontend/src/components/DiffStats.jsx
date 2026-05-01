function avg(arr, key) {
  if (!arr.length) return null;
  return arr.reduce((s, c) => s + (c[key] ?? 0), 0) / arr.length;
}

function Row({ label, valA, valB, higherIsBetter = null }) {
  const aNum = typeof valA === 'number' ? valA : null;
  const bNum = typeof valB === 'number' ? valB : null;

  const winA =
    higherIsBetter === true
      ? aNum > bNum
      : higherIsBetter === false
      ? aNum < bNum
      : false;
  const winB =
    higherIsBetter === true
      ? bNum > aNum
      : higherIsBetter === false
      ? bNum < aNum
      : false;

  const clsA = winA ? 'text-emerald-400 font-semibold' : 'text-slate-300';
  const clsB = winB ? 'text-emerald-400 font-semibold' : 'text-slate-300';

  return (
    <tr className="border-t border-slate-700">
      <td className="py-1 pr-3 text-slate-400">{label}</td>
      <td className={`py-1 text-center ${clsA}`}>{valA ?? '—'}</td>
      <td className={`py-1 text-center ${clsB}`}>{valB ?? '—'}</td>
    </tr>
  );
}

export default function DiffStats({ chunksA, chunksB }) {
  if (!chunksA.length && !chunksB.length) return null;

  const countA = chunksA.length || null;
  const countB = chunksB.length || null;
  const sizeA = avg(chunksA, 'char_count');
  const sizeB = avg(chunksB, 'char_count');
  const bqA = avg(chunksA, 'boundary_quality');
  const bqB = avg(chunksB, 'boundary_quality');

  return (
    <div className="mt-3 bg-slate-800 border border-slate-700 rounded-lg p-3">
      <p className="text-[11px] uppercase text-slate-400 tracking-wide mb-2">Diff Stats</p>
      <table className="w-full text-[12px]">
        <thead>
          <tr>
            <th className="text-left text-slate-500 font-normal pb-1">Metric</th>
            <th className="text-center text-indigo-400 font-semibold pb-1">A</th>
            <th className="text-center text-amber-400 font-semibold pb-1">B</th>
          </tr>
        </thead>
        <tbody>
          <Row label="Chunks" valA={countA} valB={countB} higherIsBetter={false} />
          <Row
            label="Avg size (chars)"
            valA={sizeA !== null ? sizeA.toFixed(0) : null}
            valB={sizeB !== null ? sizeB.toFixed(0) : null}
          />
          <Row
            label="Avg boundary quality"
            valA={bqA !== null ? bqA.toFixed(2) : null}
            valB={bqB !== null ? bqB.toFixed(2) : null}
            higherIsBetter={true}
          />
        </tbody>
      </table>
    </div>
  );
}
