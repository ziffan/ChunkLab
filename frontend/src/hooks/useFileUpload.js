import { useState } from 'react';

const MAX_BYTES = 500 * 1024;
const VALID_EXTS = new Set(['.txt', '.md']);

export function useFileUpload(onLoad, onClear) {
  const [fileName, setFileName] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const handleFile = (file) => {
    setUploadError(null);

    const dot = file.name.lastIndexOf('.');
    const ext = dot >= 0 ? file.name.slice(dot).toLowerCase() : '';
    if (!VALID_EXTS.has(ext)) {
      setUploadError('Only .txt and .md files supported. Convert to markdown first.');
      return;
    }

    if (file.size > MAX_BYTES) {
      setUploadError(`File exceeds 500 KB (${(file.size / 1024).toFixed(0)} KB). Please reduce file size.`);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setFileName(file.name);
      onLoad(e.target.result);
    };
    reader.readAsText(file, 'utf-8');
  };

  const clearFile = () => {
    setFileName(null);
    setUploadError(null);
    onClear();
  };

  return { fileName, uploadError, handleFile, clearFile };
}
