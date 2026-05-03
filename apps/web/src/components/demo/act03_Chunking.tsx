"use client";

import { ChunkBar } from "./primitives/ChunkBar";

export function Act03Chunking({ chunks }: { chunks: number }) {
  return (
    <div className="space-y-5">
      <Metric label="Chunks emitted" value={chunks} />
      <ChunkBar total={chunks || 16} active={chunks || 16} />
      <p className="text-sm leading-6 text-text-secondary">
        Each rectangle is an overlapping source window. The replay and live path both read the same
        `chunk_document` event counts.
      </p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-border bg-background p-5">
      <p className="text-xs uppercase tracking-wide text-text-secondary">{label}</p>
      <p className="mt-2 text-4xl font-semibold text-text-primary">{value}</p>
    </div>
  );
}
