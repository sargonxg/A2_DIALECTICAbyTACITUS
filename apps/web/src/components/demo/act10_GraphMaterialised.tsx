"use client";

import { GraphSpotlight } from "./primitives/GraphSpotlight";
import type { GraphData } from "@/types/graph";

export function Act10GraphMaterialised({
  graph,
  nodesWritten,
  edgesWritten,
}: {
  graph: GraphData;
  nodesWritten: number;
  edgesWritten: number;
}) {
  return (
    <div className="space-y-4">
      <GraphSpotlight graph={graph} />
      <div className="grid gap-3 md:grid-cols-2">
        <Metric label="Nodes written" value={nodesWritten} />
        <Metric label="Edges written" value={edgesWritten} />
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-border bg-background p-4">
      <p className="text-xs uppercase tracking-wide text-text-secondary">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-text-primary">{value}</p>
    </div>
  );
}
