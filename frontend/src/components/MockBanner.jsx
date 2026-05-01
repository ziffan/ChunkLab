export default function MockBanner() {
  return (
    <div className="w-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[12px] px-4 py-1.5 flex items-center gap-2">
      <span>⚠️</span>
      <span>
        Token counts are estimated (mock mode). Set{' '}
        <code className="bg-amber-500/20 px-1 rounded">MOCK_MODE=false</code>{' '}
        in <code className="bg-amber-500/20 px-1 rounded">.env</code> for real tokenization.
      </span>
    </div>
  );
}
