import { useState } from 'react';
import { fetchOpenApiSpec } from '../services/api';

export default function ApiReferenceButton() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDownload = async () => {
    setLoading(true);
    setError(null);
    try {
      const spec = await fetchOpenApiSpec();
      const blob = new Blob([JSON.stringify(spec, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'chunklab_openapi.json';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError('Backend offline');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex items-center gap-1">
      <button
        onClick={handleDownload}
        disabled={loading}
        title="Download OpenAPI spec (JSON)"
        className="h-7 px-3 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-slate-300 rounded text-[12px] transition-colors"
      >
        {loading ? 'Fetching…' : 'API Spec'}
      </button>
      {error && (
        <span className="text-red-400 text-[11px]">{error}</span>
      )}
    </div>
  );
}
