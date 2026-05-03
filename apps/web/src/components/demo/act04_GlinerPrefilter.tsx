"use client";

import { ChunkBar } from "./primitives/ChunkBar";

export function Act04GlinerPrefilter({ chunks, avgDensity }: { chunks: number; avgDensity: number }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-3 md:grid-cols-2">
        <Metric label="Scored chunks" value={chunks} />
        <Metric label="Avg entity density" value={avgDensity.toFixed(2)} />
      </div>
      <ChunkBar total={chunks || 16} active={Math.max(1, Math.round((chunks || 16) * 0.7))} />
      <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm leading-6 text-amber-100">
        Low-density chunks can be routed through cheaper extraction paths; the graph keeps the audit trail.
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-border bg-background p-5">
      <p className="text-xs uppercase tracking-wide text-text-secondary">{label}</p>
      <p className="mt-2 text-4xl font-semibold text-text-primary">{value}</p>
    </div>
  );
}
