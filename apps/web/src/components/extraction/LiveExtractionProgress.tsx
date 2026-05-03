"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Check, CircleAlert, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

// Canonical ordering must match packages/api/.../services/pipeline_runner.py:PIPELINE_STEPS.
const PIPELINE_STEPS: Array<{ key: string; label: string }> = [
  { key: "fetch_gutenberg", label: "Fetch source" },
  { key: "chunk_document", label: "Chunk document" },
  { key: "gliner_prefilter", label: "GLiNER pre-filter" },
  { key: "extract_entities", label: "Extract entities" },
  { key: "validate_schema", label: "Validate schema" },
  { key: "extract_relationships", label: "Extract relationships" },
  { key: "resolve_coreference", label: "Resolve coreference" },
  { key: "validate_structural", label: "Structural validation" },
  { key: "compute_embeddings", label: "Compute embeddings" },
  { key: "check_review_needed", label: "Review check" },
  { key: "write_to_graph", label: "Write to graph" },
];

interface ProgressEvent {
  job_id: string;
  step: string;
  status: string;
  message?: string;
  counts?: Record<string, number>;
  timestamp?: number;
}

type StepState = "pending" | "active" | "complete" | "failed";

interface Props {
  workspaceId: string;
  jobId: string;
  onComplete?: (job: Record<string, unknown>) => void;
}

export default function LiveExtractionProgress({
  workspaceId,
  jobId,
  onComplete,
}: Props) {
  const [stepStates, setStepStates] = useState<Record<string, StepState>>({});
  const [stepCounts, setStepCounts] = useState<Record<string, Record<string, number>>>({});
  const [terminal, setTerminal] = useState<"running" | "complete" | "failed">("running");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [finalJob, setFinalJob] = useState<Record<string, unknown> | null>(null);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    if (!jobId) return;
    const source = api.streamExtraction(workspaceId, jobId);

    const apply = (raw: MessageEvent<string>) => {
      try {
        const evt = JSON.parse(raw.data) as ProgressEvent;
        if (evt.step === "stream" && evt.status === "ready") return;
        if (evt.step === "job") {
          if (evt.status === "complete") setTerminal("complete");
          if (evt.status === "failed") {
            setTerminal("failed");
            setErrorMessage(evt.message ?? "Extraction failed");
          }
          return;
        }
        setStepStates((prev) => ({
          ...prev,
          [evt.step]:
            evt.status === "complete"
              ? "complete"
              : evt.status === "failed"
                ? "failed"
                : "active",
        }));
        if (evt.counts && Object.keys(evt.counts).length > 0) {
          setStepCounts((prev) => ({ ...prev, [evt.step]: evt.counts! }));
        }
      } catch {
        // ignore malformed frames
      }
    };

    source.addEventListener("started", apply);
    source.addEventListener("complete", apply);
    source.addEventListener("failed", apply);
    source.addEventListener("info", apply);
    source.addEventListener("ready", apply);

    source.addEventListener("job", (raw) => {
      try {
        const payload = JSON.parse((raw as MessageEvent<string>).data) as {
          job: Record<string, unknown>;
        };
        setFinalJob(payload.job);
        if (payload.job.status === "complete") {
          setTerminal("complete");
          onCompleteRef.current?.(payload.job);
        } else if (payload.job.status === "failed") {
          setTerminal("failed");
          setErrorMessage((payload.job.error as string) ?? "Extraction failed");
        }
      } catch {
        // ignore
      }
    });

    source.onerror = () => {
      // EventSource will retry; only treat as failure once we know the job is terminal.
    };

    return () => {
      source.close();
    };
  }, [workspaceId, jobId]);

  const headlineCounts = useMemo(() => {
    const writeCounts = stepCounts["write_to_graph"] ?? {};
    return {
      chunks: stepCounts["chunk_document"]?.["chunks"] ?? 0,
      entitiesRaw: stepCounts["extract_entities"]?.["entities_raw"] ?? 0,
      entitiesValid: stepCounts["validate_schema"]?.["entities_valid"] ?? 0,
      edges: stepCounts["extract_relationships"]?.["edges_valid"] ?? 0,
      nodesWritten: writeCounts["nodes_written"] ?? 0,
      edgesWritten: writeCounts["edges_written"] ?? 0,
    };
  }, [stepCounts]);

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-text-primary">Extraction Pipeline</h3>
        <span
          className={cn(
            "text-xs px-2 py-0.5 rounded",
            terminal === "running"
              ? "bg-accent/10 text-accent"
              : terminal === "complete"
                ? "bg-success/10 text-success"
                : "bg-danger/10 text-danger",
          )}
        >
          {terminal}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
        <Tile label="Chunks" value={headlineCounts.chunks} />
        <Tile label="Entities (raw)" value={headlineCounts.entitiesRaw} />
        <Tile label="Entities (valid)" value={headlineCounts.entitiesValid} />
        <Tile label="Relationships" value={headlineCounts.edges} />
        <Tile label="Nodes written" value={headlineCounts.nodesWritten} />
        <Tile label="Edges written" value={headlineCounts.edgesWritten} />
      </div>

      <div className="space-y-1.5">
        {PIPELINE_STEPS.map((step) => {
          const state = stepStates[step.key] ?? "pending";
          const counts = stepCounts[step.key];
          return (
            <div key={step.key} className="flex items-center gap-3">
              <StepIcon state={state} />
              <span
                className={cn(
                  "text-sm flex-1",
                  state === "complete"
                    ? "text-text-primary"
                    : state === "active"
                      ? "text-accent"
                      : state === "failed"
                        ? "text-danger"
                        : "text-text-secondary",
                )}
              >
                {step.label}
              </span>
              {counts && (
                <span className="text-[11px] text-text-secondary tabular-nums">
                  {Object.entries(counts)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(" · ")}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {errorMessage && (
        <div className="flex items-start gap-2 text-sm text-danger">
          <CircleAlert size={14} className="mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      {finalJob && terminal === "complete" && (
        <div className="text-xs text-text-secondary">
          Job <code className="text-text-primary">{String(finalJob.job_id)}</code> completed
          in {String(finalJob.completed_at ?? "")}.
        </div>
      )}
    </div>
  );
}

function StepIcon({ state }: { state: StepState }) {
  if (state === "complete")
    return (
      <span className="w-5 h-5 rounded-full bg-success text-white flex items-center justify-center">
        <Check size={11} />
      </span>
    );
  if (state === "active")
    return (
      <span className="w-5 h-5 rounded-full bg-accent text-white flex items-center justify-center">
        <Loader2 size={11} className="animate-spin" />
      </span>
    );
  if (state === "failed")
    return (
      <span className="w-5 h-5 rounded-full bg-danger text-white flex items-center justify-center">
        !
      </span>
    );
  return <span className="w-5 h-5 rounded-full bg-surface-hover" />;
}

function Tile({ label, value }: { label: string; value: number }) {
  return (
    <div className="px-2.5 py-1.5 rounded border border-border">
      <div className="text-[10px] uppercase tracking-wide text-text-secondary">{label}</div>
      <div className="text-sm font-semibold text-text-primary tabular-nums">{value}</div>
    </div>
  );
}
