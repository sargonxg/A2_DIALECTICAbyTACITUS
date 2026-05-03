import { Route } from "lucide-react";
import type { GraphData } from "@/types/graph";
import type { CuratedReasoningQuestion } from "./types";

interface Props {
  question: CuratedReasoningQuestion;
  graph: GraphData;
}

export function PathHighlightOverlay({ question, graph }: Props) {
  const nodes = graph.nodes.filter((node) => question.dialectica.cited_node_ids.includes(node.id));
  const edges = graph.links.filter((edge) => question.dialectica.cited_edge_ids.includes(edge.id));

  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
        <Route className="h-4 w-4 text-accent" aria-hidden="true" />
        Citation path
      </div>
      <div className="grid gap-2 text-xs text-text-secondary sm:grid-cols-2">
        <div>
          <p className="mb-1 font-semibold text-text-primary">Nodes</p>
          <div className="flex flex-wrap gap-1.5">
            {nodes.map((node) => (
              <span key={node.id} className="rounded-md bg-background px-2 py-1">
                {node.name}
              </span>
            ))}
          </div>
        </div>
        <div>
          <p className="mb-1 font-semibold text-text-primary">Edges</p>
          <div className="flex flex-wrap gap-1.5">
            {edges.map((edge) => (
              <span key={edge.id} className="rounded-md bg-background px-2 py-1">
                {edge.edge_type}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
