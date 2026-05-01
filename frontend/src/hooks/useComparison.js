import { useState, useEffect, useRef } from 'react';
import { useDebounce } from './useDebounce';
import { chunkMarkdown } from '../services/api';

function buildBody(markdown, config, regexPatterns) {
  const filtered = regexPatterns.filter((p) => p.label && p.pattern);
  const body = { markdown, regex_patterns: filtered, strategy: config.strategy };
  if (config.strategy === 'fixed') {
    body.chunk_size = config.chunk_size;
    body.chunk_overlap = config.chunk_overlap;
  } else if (config.strategy === 'recursive') {
    body.chunk_size = config.chunk_size;
    body.chunk_overlap = config.chunk_overlap;
    body.strategy_params = config.strategyParams?.separators
      ? { separators: config.strategyParams.separators }
      : {};
  } else {
    body.strategy_params = config.strategyParams || {};
  }
  return body;
}

function useConfigChunker(markdown, config, regexPatterns) {
  const [chunks, setChunks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const debouncedMarkdown = useDebounce(markdown, 500);
  const requestIdRef = useRef(0);
  const configKey = JSON.stringify(config);

  useEffect(() => {
    const reqId = ++requestIdRef.current;
    if (!debouncedMarkdown) {
      setChunks([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    chunkMarkdown(buildBody(debouncedMarkdown, config, regexPatterns))
      .then((data) => {
        if (reqId !== requestIdRef.current) return;
        setChunks(data.chunks || []);
        setIsLoading(false);
      })
      .catch(() => {
        if (reqId !== requestIdRef.current) return;
        setChunks([]);
        setIsLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedMarkdown, configKey, regexPatterns]);

  return { chunks, isLoading };
}

export function useComparison(markdown, configA, configB, regexPatterns) {
  const a = useConfigChunker(markdown, configA, regexPatterns);
  const b = useConfigChunker(markdown, configB, regexPatterns);
  return {
    chunksA: a.chunks,
    isLoadingA: a.isLoading,
    chunksB: b.chunks,
    isLoadingB: b.isLoading,
  };
}

export function defaultConfig(overrides = {}) {
  return {
    strategy: 'fixed',
    chunk_size: 512,
    chunk_overlap: 50,
    strategyParams: {},
    ...overrides,
  };
}
