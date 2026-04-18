import { useState, useCallback } from 'react';
import { estimateTokens } from '../services/api';

export function useTokenization() {
  const [provider, setProvider] = useState('mock');
  const [modelName, setModelName] = useState('mock');
  const [tokenCounts, setTokenCounts] = useState([]);
  const [isTokenizing, setIsTokenizing] = useState(false);
  const [tokenizeError, setTokenizeError] = useState(null);
  const [isMockToken, setIsMockToken] = useState(true);

  const handleEstimateTokens = useCallback(async (chunks) => {
    if (chunks.length === 0) return;
    setIsTokenizing(true);
    setTokenizeError(null);
    try {
      const result = await estimateTokens({
        texts: chunks.map((c) => c.text),
        provider,
        model_name: modelName,
      });
      setTokenCounts(result.token_counts);
      setIsMockToken(result.is_mock);
      if (result.error) {
        setTokenizeError(result.error.message);
      }
    } catch (err) {
      setTokenizeError(err.message);
    } finally {
      setIsTokenizing(false);
    }
  }, [provider, modelName]);

  return {
    provider,
    setProvider,
    modelName,
    setModelName,
    tokenCounts,
    isTokenizing,
    tokenizeError,
    isMockToken,
    handleEstimateTokens,
  };
}
