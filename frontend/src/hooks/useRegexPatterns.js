import { useState, useCallback, useMemo } from 'react';
import { testRegexPattern } from '../services/api';

export function useRegexPatterns(initialPatterns = [], markdown = '') {
  const [regexPatterns, setRegexPatterns] = useState(initialPatterns);

  const cleanPatterns = useMemo(
    () =>
      regexPatterns.map((p) => ({
        id: p.id,
        label: p.label,
        pattern: p.pattern,
      })),
    [regexPatterns]
  );

  const handleAddPattern = useCallback(() => {
    let id;
    try {
      id = crypto.randomUUID();
    } catch (e) {
      id = Math.random().toString(36).substring(2, 15);
    }
    setRegexPatterns((prev) => [
      ...prev,
      { id, label: '', pattern: '', testResult: null, testError: null },
    ]);
  }, []);

  const handleRemovePattern = useCallback((id) => {
    setRegexPatterns((prev) => prev.filter((p) => p.id !== id));
  }, []);

  const handleLabelChange = useCallback((id, label) => {
    setRegexPatterns((prev) =>
      prev.map((p) => (p.id === id ? { ...p, label, testResult: null, testError: null } : p))
    );
  }, []);

  const handlePatternChange = useCallback((id, pattern) => {
    setRegexPatterns((prev) =>
      prev.map((p) => (p.id === id ? { ...p, pattern, testResult: null, testError: null } : p))
    );
  }, []);

  const handleTestPattern = useCallback(
    async (id) => {
      const pat = regexPatterns.find((p) => p.id === id);
      if (!pat || !pat.pattern) return;
      try {
        const result = await testRegexPattern({ pattern: pat.pattern, text: markdown });
        setRegexPatterns((prev) =>
          prev.map((p) => (p.id === id ? { ...p, testResult: result, testError: null } : p))
        );
      } catch (err) {
        setRegexPatterns((prev) =>
          prev.map((p) => (p.id === id ? { ...p, testResult: null, testError: err.message } : p))
        );
      }
    },
    [regexPatterns, markdown]
  );

  return {
    regexPatterns,
    cleanPatterns,
    handleAddPattern,
    handleRemovePattern,
    handleLabelChange,
    handlePatternChange,
    handleTestPattern,
  };
}
