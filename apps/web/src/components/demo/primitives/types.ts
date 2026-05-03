import type { GraphData } from "@/types/graph";

export interface PipelineEvent {
  job_id: string;
  step: string;
  status: "ready" | "started" | "complete" | "failed" | "info" | string;
  message?: string;
  counts?: Record<string, number>;
  timestamp?: number;
  job?: Record<string, unknown>;
  graph?: GraphData;
}

export interface ReplayFrame {
  t: number;
  event: string;
  data: PipelineEvent;
}

export type DemoMode = "idle" | "live" | "replay" | "failed";
