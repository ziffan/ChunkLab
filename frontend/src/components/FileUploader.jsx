import { useRef, useState } from 'react';
import { useFileUpload } from '../hooks/useFileUpload';

export default function FileUploader({ onLoad, onClear }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const { fileName, uploadError, handleFile, clearFile } = useFileUpload(onLoad, onClear);

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  return (
    <div className="mb-2 space-y-1.5">
      {!fileName ? (
        <div
          onClick={() => inputRef.current?.click()}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={() => setIsDragging(false)}
          className={`border-2 border-dashed rounded-lg py-3 text-center cursor-pointer transition-colors select-none ${
            isDragging
              ? 'border-indigo-400 bg-indigo-500/10 text-indigo-300'
              : 'border-slate-600 hover:border-slate-500 text-slate-400'
          }`}
        >
          <p className="text-[12px]">Drop <code>.txt</code> / <code>.md</code> here, or click to browse</p>
          <input
            ref={inputRef}
            type="file"
            accept=".txt,.md,text/plain,text/markdown"
            onChange={(e) => {
              const file = e.target.files[0];
              if (file) handleFile(file);
              e.target.value = '';
            }}
            className="hidden"
          />
        </div>
      ) : (
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg">
          <span className="text-slate-400 text-[12px]">📄</span>
          <span className="text-[12px] text-slate-200 truncate flex-1">{fileName}</span>
          <button
            onClick={clearFile}
            title="Clear file"
            className="text-slate-500 hover:text-slate-100 text-[16px] leading-none flex-shrink-0"
          >
            ×
          </button>
        </div>
      )}
      {uploadError && (
        <p className="text-[11px] text-red-400 px-1">{uploadError}</p>
      )}
    </div>
  );
}
