"use client";

import { useCallback, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { BookOpen, FileUp, Library } from "lucide-react";
import DocumentUpload from "@/components/extraction/DocumentUpload";
import GutenbergPicker from "@/components/extraction/GutenbergPicker";
import LiveExtractionProgress from "@/components/extraction/LiveExtractionProgress";
import AutoReasoningPanel from "@/components/extraction/AutoReasoningPanel";
import { api } from "@/lib/api";
import type { OntologyTier } from "@/types/ontology";

type Mode = "gutenberg" | "upload";

export default function IngestPage() {
  const { id } = useParams();
  const workspaceId = id as string;

  const [mode, setMode] = useState<Mode>("gutenberg");
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [activeTitle, setActiveTitle] = useState<string>("");
  const [autoReasoning, setAutoReasoning] = useState<Record<string, unknown> | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const startJob = useCallback(
    (jobId: string, title: string) => {
      setActiveJobId(jobId);
      setActiveTitle(title);
      setAutoReasoning(null);
      setSubmitError(null);
    },
    [],
  );

  const handleGutenberg = async (params: {
    book_id: string;
    title: string;
    tier: OntologyTier;
    max_chars: number;
  }) => {
    try {
      const res = await api.ingestGutenberg(workspaceId, {
        book_id: params.book_id,
        title: params.title,
        tier: params.tier,
        max_chars: params.max_chars,
      });
      startJob(res.job_id, res.title);
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Could not start Gutenberg ingest.");
    }
  };

  const handleUpload = async (data: {
    text?: string;
    files?: File[];
    tier: OntologyTier;
  }) => {
    try {
      if (data.files && data.files.length > 0) {
        const file = data.files[0];
        const res = await api.uploadDocument(workspaceId, file, data.tier);
        startJob(res.id, file.name);
        return;
      }
      if (data.text) {
        const res = await api.extract({
          workspace_id: workspaceId,
          text: data.text,
          tier: data.tier,
        });
        startJob(res.id, "Pasted text");
      }
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Upload failed.");
    }
  };

  const handleComplete = (job: Record<string, unknown>) => {
    const reasoning = (job as { auto_reasoning?: Record<string, unknown> }).auto_reasoning;
    if (reasoning) setAutoReasoning(reasoning);
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">Ingest Sources</h2>
          <p className="text-xs text-text-secondary">
            Pick a Project Gutenberg classic, upload a document, or paste text.
          </p>
        </div>
        <Link
          href={`/workspaces/${workspaceId}/corpus`}
          className="text-xs flex items-center gap-1.5 text-text-secondary hover:text-accent"
        >
          <Library size={14} /> Corpus library
        </Link>
      </div>

      <div className="flex gap-1 border-b border-border">
        <TabButton
          active={mode === "gutenberg"}
          onClick={() => setMode("gutenberg")}
          icon={<BookOpen size={14} />}
          label="Project Gutenberg"
        />
        <TabButton
          active={mode === "upload"}
          onClick={() => setMode("upload")}
          icon={<FileUp size={14} />}
          label="Upload / Paste"
        />
      </div>

      {submitError && (
        <div className="text-sm text-danger border-l-2 border-danger pl-3">{submitError}</div>
      )}

      {mode === "gutenberg" && <GutenbergPicker onIngest={handleGutenberg} />}
      {mode === "upload" && (
        <DocumentUpload workspaceId={workspaceId} onSubmit={handleUpload} />
      )}

      {activeJobId && (
        <div className="space-y-4">
          <div className="text-xs text-text-secondary">
            Ingesting <strong className="text-text-primary">{activeTitle}</strong>
          </div>
          <LiveExtractionProgress
            workspaceId={workspaceId}
            jobId={activeJobId}
            onComplete={handleComplete}
          />
          <AutoReasoningPanel
            reasoning={autoReasoning as Parameters<typeof AutoReasoningPanel>[0]["reasoning"]}
          />
        </div>
      )}
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-2 text-sm border-b-2 transition-colors ${
        active
          ? "border-accent text-accent"
          : "border-transparent text-text-secondary hover:text-text-primary"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
