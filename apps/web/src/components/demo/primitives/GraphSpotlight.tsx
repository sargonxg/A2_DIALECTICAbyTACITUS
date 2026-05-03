"use client";

import ForceGraph from "@/components/graph/ForceGraph";
import type { GraphData } from "@/types/graph";

export function GraphSpotlight({ graph }: { graph: GraphData }) {
  if (!graph.nodes.length) {
    return (
      <div className="flex h-[420px] items-center justify-center rounded-lg border border-border bg-background text-sm text-text-secondary">
        Graph will materialize when the stream reaches write_to_graph.
      </div>
    );
  }
  return (
    <div className="rounded-lg border border-border bg-background p-2">
      <ForceGraph data={graph} width={900} height={420} />
    </div>
  );
}
