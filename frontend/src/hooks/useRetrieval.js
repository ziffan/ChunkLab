import { useState } from 'react';
import { retrieveChunks } from '../services/api';

export function useRetrieval() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isUnavailable, setIsUnavailable] = useState(false);

  const retrieve = async (chunks) => {
    if (!query.trim() || !chunks.length) return;
    setIsLoading(true);
    setError(null);
    setIsUnavailable(false);
    try {
      const data = await retrieveChunks({
        query: query.trim(),
        chunks: chunks.map((c) => ({ index: c.index, text: c.text })),
        top_k: 5,
      });
      setResults(data.results || []);
    } catch (err) {
      if (err.status === 503) {
        setIsUnavailable(true);
        setResults([]);
      } else {
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError(null);
    setIsUnavailable(false);
  };

  return { query, setQuery, results, isLoading, error, isUnavailable, retrieve, clearResults };
}
