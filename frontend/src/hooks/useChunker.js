import { useState, useEffect, useRef } from 'react';
import { useDebounce } from './useDebounce';
import { chunkMarkdown } from '../services/api';

export function useChunker(markdown, params, regexPatterns) {
  const [chunks, setChunks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const debouncedMarkdown = useDebounce(markdown, 500);
  const requestIdRef = useRef(0);

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

    chunkMarkdown({
      markdown: debouncedMarkdown,
      chunk_size: params.chunk_size,
      chunk_overlap: params.chunk_overlap,
      regex_patterns: filtered,
    })
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
  }, [debouncedMarkdown, params.chunk_size, params.chunk_overlap, regexPatterns]);

  return { chunks, isLoading, error };
}
