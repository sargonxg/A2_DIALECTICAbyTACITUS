"use client";

import { Loader2, Check, X } from "lucide-react";

interface ExtractionJob {
  id: string;
  workspace_name: string;
  status: "pending" | "processing" | "completed" | "failed";
  nodes_extracted: number;
  created_at: string;
}

interface Props {
  jobs: ExtractionJob[];
}

export default function PipelineMonitor({ jobs }: Props) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Extraction Queue</h3>
      <div className="space-y-2">
        {jobs.map((job) => (
          <div key={job.id} className="flex items-center gap-3 text-sm">
            {job.status === "processing" && <Loader2 size={14} className="text-accent animate-spin" />}
            {job.status === "completed" && <Check size={14} className="text-success" />}
            {job.status === "failed" && <X size={14} className="text-danger" />}
            {job.status === "pending" && <div className="w-3.5 h-3.5 rounded-full bg-surface-hover" />}
            <span className="text-text-primary flex-1">{job.workspace_name}</span>
            <span className="font-mono text-xs text-text-secondary">{job.nodes_extracted} nodes</span>
            <span className="badge bg-surface-hover text-text-secondary text-[10px]">{job.status}</span>
          </div>
        ))}
        {jobs.length === 0 && <p className="text-sm text-text-secondary">No active jobs</p>}
      </div>
    </div>
  );
}
