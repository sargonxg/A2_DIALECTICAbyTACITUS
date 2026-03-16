"use client";

import { useState, useCallback } from "react";
import {
  RefreshCw,
  GitBranch,
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  Circle,
} from "lucide-react";

type JobStatus = "pending" | "running" | "complete" | "failed";

interface PipelineJob {
  id: string;
  type: string;
  workspace: string;
  status: JobStatus;
  progress: number;
  durationMs: number | null;
  startedAt: string;
}

const MOCK_JOBS: PipelineJob[] = [
  {
    id: "job-0a1f2b",
    type: "entity-extraction",
    workspace: "JCPOA Nuclear Negotiations",
    status: "complete",
    progress: 100,
    durationMs: 4230,
    startedAt: "2026-03-16T08:12:00Z",
  },
  {
    id: "job-1c3d4e",
    type: "relation-detection",
    workspace: "JCPOA Nuclear Negotiations",
    status: "complete",
    progress: 100,
    durationMs: 2810,
    startedAt: "2026-03-16T08:12:05Z",
  },
  {
    id: "job-2e5f6a",
    type: "entity-extraction",
    workspace: "HR Workplace Mediation",
    status: "running",
    progress: 62,
    durationMs: null,
    startedAt: "2026-03-16T08:30:11Z",
  },
  {
    id: "job-3b7c8d",
    type: "escalation-scoring",
    workspace: "HR Workplace Mediation",
    status: "pending",
    progress: 0,
    durationMs: null,
    startedAt: "2026-03-16T08:30:00Z",
  },
  {
    id: "job-4d9e0f",
    type: "trust-graph-build",
    workspace: "Commercial Contract Dispute",
    status: "failed",
    progress: 33,
    durationMs: 1540,
    startedAt: "2026-03-16T07:55:20Z",
  },
];

const STATUS_CONFIG: Record<
  JobStatus,
  { label: string; color: string; icon: React.ReactNode }
> = {
  pending: {
    label: "Pending",
    color: "text-[#71717a]",
    icon: <Clock size={13} />,
  },
  running: {
    label: "Running",
    color: "text-yellow-400",
    icon: <Loader2 size={13} className="animate-spin" />,
  },
  complete: {
    label: "Complete",
    color: "text-green-400",
    icon: <CheckCircle2 size={13} />,
  },
  failed: {
    label: "Failed",
    color: "text-red-400",
    icon: <XCircle size={13} />,
  },
};

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="w-full h-1.5 bg-[#27272a] rounded-full overflow-hidden">
      <div
        className="h-full bg-teal-600 rounded-full transition-all duration-500"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

function formatDuration(ms: number | null): string {
  if (ms === null) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export function PipelineMonitor() {
  const [jobs, setJobs] = useState<PipelineJob[]>(MOCK_JOBS);
  const [refreshing, setRefreshing] = useState(false);

  const refresh = useCallback(() => {
    setRefreshing(true);
    // Simulate a short fetch delay
    setTimeout(() => {
      // Advance running jobs slightly
      setJobs((prev) =>
        prev.map((job) =>
          job.status === "running"
            ? { ...job, progress: Math.min(100, job.progress + 5) }
            : job,
        ),
      );
      setRefreshing(false);
    }, 600);
  }, []);

  const summary = {
    total: jobs.length,
    running: jobs.filter((j) => j.status === "running").length,
    pending: jobs.filter((j) => j.status === "pending").length,
    failed: jobs.filter((j) => j.status === "failed").length,
  };

  return (
    <div className="space-y-4">
      {/* Summary row */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Total Jobs", value: summary.total, color: "text-[#fafafa]" },
          { label: "Running", value: summary.running, color: "text-yellow-400" },
          { label: "Pending", value: summary.pending, color: "text-[#71717a]" },
          { label: "Failed", value: summary.failed, color: "text-red-400" },
        ].map((s) => (
          <div
            key={s.label}
            className="bg-[#18181b] border border-[#27272a] rounded-lg p-3"
          >
            <p className="text-[#71717a] text-xs mb-1">{s.label}</p>
            <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Job list */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg">
        <div className="flex items-center justify-between px-5 py-3 border-b border-[#27272a]">
          <div className="flex items-center gap-2">
            <GitBranch size={15} className="text-[#71717a]" />
            <h3 className="text-[#fafafa] text-sm font-semibold">Pipeline Jobs</h3>
          </div>
          <button
            onClick={refresh}
            disabled={refreshing}
            className="p-1.5 rounded-md text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors disabled:opacity-50"
            title="Refresh jobs"
            aria-label="Refresh pipeline jobs"
          >
            <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
          </button>
        </div>

        <div className="divide-y divide-[#27272a]/60">
          {jobs.map((job) => {
            const cfg = STATUS_CONFIG[job.status];
            return (
              <div key={job.id} className="px-5 py-3">
                <div className="flex items-start justify-between gap-4 mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-[#fafafa] text-sm font-medium">
                        {job.type}
                      </span>
                      <span className={`flex items-center gap-1 text-xs ${cfg.color}`}>
                        {cfg.icon}
                        {cfg.label}
                      </span>
                    </div>
                    <p className="text-[#71717a] text-xs truncate">{job.workspace}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-[#52525b] text-xs font-mono">{job.id}</p>
                    <p className="text-[#71717a] text-xs mt-0.5">
                      {formatDuration(job.durationMs)}
                    </p>
                  </div>
                </div>
                {(job.status === "running" ||
                  job.status === "complete" ||
                  job.status === "failed") && (
                  <div className="flex items-center gap-2">
                    <ProgressBar value={job.progress} />
                    <span className="text-[#71717a] text-xs w-8 text-right flex-shrink-0">
                      {job.progress}%
                    </span>
                  </div>
                )}
                {job.status === "pending" && (
                  <div className="flex items-center gap-1.5 text-[#52525b] text-xs">
                    <Circle size={8} />
                    Queued
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
