'use client';

import React, { useState, useRef, useCallback, DragEvent, ChangeEvent } from 'react';
import {
  Upload,
  FileText,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
  CloudUpload,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
const ACCEPTED = ['.pdf', '.txt', '.docx'];
const ACCEPTED_MIME = [
  'application/pdf',
  'text/plain',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

interface DocumentUploadProps {
  workspaceId: string;
  onUploadComplete: () => void;
}

export function DocumentUpload({ workspaceId, onUploadComplete }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const xhrRef = useRef<XMLHttpRequest | null>(null);

  const acceptFile = useCallback((f: File) => {
    const ext = '.' + f.name.split('.').pop()?.toLowerCase();
    if (!ACCEPTED.includes(ext) && !ACCEPTED_MIME.includes(f.type)) {
      setErrorMsg(`Unsupported file type. Accepted: ${ACCEPTED.join(', ')}`);
      return;
    }
    setFile(f);
    setStatus('idle');
    setErrorMsg(null);
    setProgress(0);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) acceptFile(dropped);
    },
    [acceptFile],
  );

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) acceptFile(selected);
  };

  const handleUpload = () => {
    if (!file || status === 'uploading') return;

    const apiKey =
      typeof window !== 'undefined'
        ? localStorage.getItem('dialectica_api_key') || ''
        : '';

    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhrRef.current = xhr;

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        setProgress(Math.round((e.loaded / e.total) * 100));
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        setStatus('success');
        setProgress(100);
        onUploadComplete();
      } else {
        setStatus('error');
        setErrorMsg(`Upload failed: HTTP ${xhr.status}`);
      }
    });

    xhr.addEventListener('error', () => {
      setStatus('error');
      setErrorMsg('Network error during upload.');
    });

    xhr.open('POST', `${API_URL}/v1/workspaces/${workspaceId}/ingest`);
    xhr.setRequestHeader('X-API-Key', apiKey);
    setStatus('uploading');
    setProgress(0);
    xhr.send(formData);
  };

  const handleCancel = () => {
    xhrRef.current?.abort();
    setStatus('idle');
    setProgress(0);
  };

  const handleClear = () => {
    setFile(null);
    setStatus('idle');
    setProgress(0);
    setErrorMsg(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onClick={() => !file && fileInputRef.current?.click()}
        className={[
          'relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed',
          'transition-all duration-200 cursor-pointer min-h-[160px] p-6',
          isDragging
            ? 'border-teal-500 bg-teal-950/20'
            : file
            ? 'border-[#27272a] bg-[#18181b] cursor-default'
            : 'border-[#27272a] bg-[#18181b] hover:border-zinc-600 hover:bg-white/[0.02]',
        ].join(' ')}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED.join(',')}
          onChange={handleFileChange}
          className="hidden"
        />

        {!file ? (
          <>
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-[#27272a] bg-[#09090b]">
              <CloudUpload className="h-5 w-5 text-zinc-500" />
            </div>
            <p className="text-sm font-medium text-zinc-300">
              Drop a document here, or{' '}
              <span className="text-teal-400 underline underline-offset-2">browse</span>
            </p>
            <p className="mt-1 text-xs text-zinc-600">
              Supports PDF, TXT, DOCX up to 50 MB
            </p>
          </>
        ) : (
          <div className="flex w-full items-center gap-3">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg border border-[#27272a] bg-[#09090b]">
              <FileText className="h-5 w-5 text-teal-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-zinc-200 truncate">{file.name}</p>
              <p className="text-xs text-zinc-500 mt-0.5">{formatBytes(file.size)}</p>
            </div>
            {status !== 'uploading' && (
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); handleClear(); }}
                className="flex-shrink-0 rounded-md p-1.5 text-zinc-500 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Progress bar */}
      {status === 'uploading' && (
        <div className="space-y-2">
          <div className="h-1.5 w-full rounded-full bg-zinc-800 overflow-hidden">
            <div
              className="h-full rounded-full bg-teal-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs text-zinc-500">
              <Loader2 className="h-3 w-3 animate-spin" />
              Uploading…
            </div>
            <span className="text-xs text-zinc-500 tabular-nums">{progress}%</span>
          </div>
        </div>
      )}

      {/* Success state */}
      {status === 'success' && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-900/40 bg-emerald-950/20 px-3 py-2.5 text-sm text-emerald-400">
          <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
          Document uploaded successfully. Extraction in progress.
        </div>
      )}

      {/* Error state */}
      {(status === 'error' || errorMsg) && (
        <div className="flex items-center gap-2 rounded-lg border border-red-900/40 bg-red-950/20 px-3 py-2.5 text-sm text-red-400">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {errorMsg ?? 'An unknown error occurred.'}
        </div>
      )}

      {/* Action buttons */}
      {file && status !== 'success' && (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleUpload}
            disabled={status === 'uploading'}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-teal-600
                       px-4 py-2.5 text-sm font-semibold text-white transition-all
                       hover:bg-teal-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {status === 'uploading' ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Uploading…
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Upload & Extract
              </>
            )}
          </button>
          {status === 'uploading' && (
            <button
              type="button"
              onClick={handleCancel}
              className="rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2.5
                         text-sm text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;