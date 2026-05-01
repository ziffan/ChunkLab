import { useState, useEffect, useRef } from 'react';
import { useDebounce } from './useDebounce';
import { chunkMarkdown } from '../services/api';

export function useChunker(markdown, params, regexPatterns, strategy = 'fixed', strategyParams = {}) {
  const [chunks, setChunks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const debouncedMarkdown = useDebounce(markdown, 500);
  const requestIdRef = useRef(0);
  const strategyParamsKey = JSON.stringify(strategyParams);

  useEffect(() => {
    const reqId = ++requestIdRef.current;

    if (debouncedMarkdown === '') {
      setChunks([]);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    const filtered = regexPatterns.filter((p) => p.label && p.pattern);

    const body = { markdown: debouncedMarkdown, regex_patterns: filtered, strategy };

    if (strategy === 'fixed') {
      body.chunk_size = params.chunk_size;
      body.chunk_overlap = params.chunk_overlap;
    } else if (strategy === 'recursive') {
      body.chunk_size = params.chunk_size;
      body.chunk_overlap = params.chunk_overlap;
      body.strategy_params = strategyParams.separators ? { separators: strategyParams.separators } : {};
    } else {
      body.strategy_params = strategyParams;
    }

    chunkMarkdown(body)
      .then((data) => {
        if (reqId !== requestIdRef.current) return;
        setChunks(data.chunks || []);
        setError(data.error);
        setIsLoading(false);
      })
      .catch((err) => {
        if (reqId !== requestIdRef.current) return;
        setError({ code: 'NETWORK_ERROR', message: err.message, pattern_id: null });
        setChunks([]);
        setIsLoading(false);
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedMarkdown, params.chunk_size, params.chunk_overlap, regexPatterns, strategy, strategyParamsKey]);

  return { chunks, isLoading, error };
}
