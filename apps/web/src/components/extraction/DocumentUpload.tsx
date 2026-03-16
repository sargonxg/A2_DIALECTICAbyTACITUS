"use client";

import { useState, useCallback } from "react";
import { Upload, FileText, Link, X } from "lucide-react";
import type { OntologyTier } from "@/types/ontology";
import OntologyTierSelector from "@/components/workspace/OntologyTierSelector";

interface Props {
  workspaceId: string;
  onSubmit: (data: { text?: string; files?: File[]; tier: OntologyTier }) => void;
}

export default function DocumentUpload({ workspaceId, onSubmit }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const [text, setText] = useState("");
  const [tier, setTier] = useState<OntologyTier>("standard");
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const dropped = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...dropped]);
  }, []);

  return (
    <div className="space-y-6">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive ? "border-accent bg-accent/5" : "border-border"}`}
      >
        <Upload size={32} className="mx-auto text-text-secondary mb-2" />
        <p className="text-text-secondary">Drop files here or <label className="text-accent cursor-pointer hover:underline">browse<input type="file" className="hidden" multiple accept=".pdf,.docx,.txt" onChange={(e) => setFiles((prev) => [...prev, ...Array.from(e.target.files || [])])} /></label></p>
        <p className="text-xs text-text-secondary mt-1">PDF, DOCX, TXT — up to 10MB</p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, i) => (
            <div key={i} className="flex items-center gap-2 card">
              <FileText size={16} className="text-text-secondary" />
              <span className="text-sm text-text-primary flex-1 truncate">{file.name}</span>
              <span className="text-xs text-text-secondary">{(file.size / 1024).toFixed(0)}KB</span>
              <button onClick={() => setFiles((f) => f.filter((_, j) => j !== i))} className="btn-ghost p-1"><X size={14} /></button>
            </div>
          ))}
        </div>
      )}

      {/* Or paste text */}
      <div>
        <label className="text-sm text-text-secondary block mb-1">Or paste text directly</label>
        <textarea value={text} onChange={(e) => setText(e.target.value)} rows={6} className="input-base w-full" placeholder="Paste conflict text for extraction..." />
      </div>

      {/* Tier selector */}
      <div>
        <label className="text-sm text-text-secondary block mb-2">Extraction Tier</label>
        <OntologyTierSelector value={tier} onChange={setTier} />
      </div>

      <button onClick={() => onSubmit({ text: text || undefined, files: files.length ? files : undefined, tier })} className="btn-primary w-full" disabled={!text && !files.length}>
        Extract Entities
      </button>
    </div>
  );
}
