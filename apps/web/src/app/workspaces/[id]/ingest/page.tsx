"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import DocumentUpload from "@/components/extraction/DocumentUpload";
import ExtractionProgress from "@/components/extraction/ExtractionProgress";
import ExtractionReview from "@/components/extraction/ExtractionReview";
import { api } from "@/lib/api";
import type { OntologyTier } from "@/types/ontology";

type Stage = "upload" | "progress" | "review";

export default function IngestPage() {
  const { id } = useParams();
  const [stage, setStage] = useState<Stage>("upload");
  const [currentStep, setCurrentStep] = useState(0);
  const [status, setStatus] = useState<"processing" | "completed" | "failed">("processing");

  const handleSubmit = async (data: { text?: string; tier: OntologyTier }) => {
    if (!data.text) return;
    setStage("progress");
    setStatus("processing");
    try {
      const interval = setInterval(() => {
        setCurrentStep((s) => { if (s >= 7) { clearInterval(interval); return s; } return s + 1; });
      }, 800);

      await api.extract({ workspace_id: id as string, text: data.text, tier: data.tier });
      setStatus("completed");
      setStage("review");
    } catch {
      setStatus("failed");
    }
  };

  return (
    <div className="max-w-3xl space-y-6">
      <h2 className="text-lg font-semibold text-text-primary">Ingest Documents</h2>

      {stage === "upload" && (
        <DocumentUpload workspaceId={id as string} onSubmit={handleSubmit} />
      )}

      {stage === "progress" && (
        <div className="space-y-4">
          <ExtractionProgress currentStep={currentStep} status={status} />
          {status === "completed" && (
            <button onClick={() => setStage("review")} className="btn-primary">Review Extracted Entities</button>
          )}
        </div>
      )}

      {stage === "review" && (
        <ExtractionReview
          entities={[]}
          onCommit={() => setStage("upload")}
          onReject={() => setStage("upload")}
        />
      )}
    </div>
  );
}
