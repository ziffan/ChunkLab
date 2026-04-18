import { useState, useEffect, useCallback } from 'react';
import { PROVIDERS } from '../constants/models';
import { fetchModels } from '../services/api';

const NEEDS_API_KEY = ['openai', 'openrouter', 'gemini', 'anthropic'];

export default function ModelSelector({ provider, modelName, onProviderChange, onModelNameChange, onEstimate }) {
  const [detectedModels, setDetectedModels] = useState([]);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectError, setDetectError] = useState(null);
  const [isAvailable, setIsAvailable] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [apiKeySaved, setApiKeySaved] = useState(false);

  const detectModelsForProvider = useCallback(async (prov, key = null) => {
    if (prov === 'mock') {
      setDetectedModels([{ id: 'mock', name: 'mock' }]);
      setIsAvailable(true);
      setDetectError(null);
      return;
    }

    setIsDetecting(true);
    setDetectError(null);
    try {
      const result = await fetchModels(prov, key);
      setIsAvailable(result.available);
      setDetectedModels(result.models || []);
      setDetectError(result.error || null);
    } catch (err) {
      setIsAvailable(false);
      setDetectedModels([]);
      setDetectError(err.message);
    } finally {
      setIsDetecting(false);
    }
  }, []);

  useEffect(() => {
    if (provider === 'mock') {
      setDetectedModels([{ id: 'mock', name: 'mock' }]);
      setIsAvailable(true);
      setDetectError(null);
      setApiKeySaved(false);
      return;
    }

    if (NEEDS_API_KEY.includes(provider)) {
      if (apiKeySaved && apiKey) {
        detectModelsForProvider(provider, apiKey);
      } else {
        detectModelsForProvider(provider);
      }
    } else {
      detectModelsForProvider(provider);
    }
    setApiKeySaved(false);
  }, [provider, apiKeySaved]);

  const handleProviderChange = (e) => {
    const newId = e.target.value;
    onProviderChange(newId);
    const found = PROVIDERS.find((p) => p.id === newId);
    if (found) {
      onModelNameChange(found.defaultModel);
    }
    setApiKey('');
    setApiKeySaved(false);
    setDetectedModels([]);
    setIsAvailable(null);
    setDetectError(null);
  };

  const handleModelSelect = (e) => {
    onModelNameChange(e.target.value);
  };

  const handleSaveApiKey = () => {
    if (apiKey.trim()) {
      setApiKeySaved(true);
    }
  };

  const handleRefresh = () => {
    if (NEEDS_API_KEY.includes(provider) && apiKey) {
      detectModelsForProvider(provider, apiKey);
    } else {
      detectModelsForProvider(provider);
    }
  };

  const needsKey = NEEDS_API_KEY.includes(provider);
  const showModelDropdown = detectedModels.length > 0 && provider !== 'mock';

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-[12px] uppercase text-slate-400 mb-1">Provider</label>
        <select
          value={provider}
          onChange={handleProviderChange}
          className="w-full h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
        >
          {PROVIDERS.map((p) => (
            <option key={p.id} value={p.id}>{p.label}</option>
          ))}
        </select>
      </div>

      {needsKey && (
        <div>
          <label className="block text-[12px] uppercase text-slate-400 mb-1">API Key</label>
          <div className="flex gap-2">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={apiKeySaved ? 'Key tersimpan' : 'Masukkan API key...'}
              className="flex-1 h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
            />
            <button
              onClick={handleSaveApiKey}
              disabled={!apiKey.trim()}
              className="h-9 px-3 bg-slate-600 hover:bg-slate-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded text-[12px] whitespace-nowrap"
            >
              Simpan
            </button>
          </div>
        </div>
      )}

      <div>
        <div className="flex items-center justify-between mb-1">
          <label className="block text-[12px] uppercase text-slate-400">Model</label>
          <div className="flex items-center gap-2">
            {isAvailable === true && (
              <span className="text-[10px] text-green-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                Terhubung
              </span>
            )}
            {isAvailable === false && (
              <span className="text-[10px] text-red-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-red-400 inline-block" />
                Tidak terhubung
              </span>
            )}
            <button
              onClick={handleRefresh}
              disabled={isDetecting}
              className="text-[10px] text-slate-400 hover:text-slate-200 disabled:opacity-50"
              title="Deteksi ulang model"
            >
              {isDetecting ? '...' : 'Refresh'}
            </button>
          </div>
        </div>

        {showModelDropdown ? (
          <select
            value={modelName}
            onChange={handleModelSelect}
            className="w-full h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
          >
            {detectedModels.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        ) : (
          <input
            type="text"
            value={modelName}
            onChange={(e) => onModelNameChange(e.target.value)}
            className="w-full h-9 bg-slate-700 border border-slate-600 text-slate-100 rounded px-2 text-[13px]"
          />
        )}
      </div>

      {detectError && (
        <div className="text-[11px] text-amber-400 bg-amber-900/30 rounded px-2 py-1">
          {detectError}
        </div>
      )}

      <button
        onClick={onEstimate}
        className="w-full h-9 bg-indigo-500 hover:bg-indigo-600 text-white rounded text-[13px] font-medium"
      >
        Estimate Tokens
      </button>
    </div>
  );
}
