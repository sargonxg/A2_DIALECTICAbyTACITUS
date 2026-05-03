"use client";

import { ChevronDown, ChevronUp, Code2, Network, Sigma, SquareCode } from "lucide-react";
import type { CuratedReasoningQuestion } from "./types";

interface Props {
  question: CuratedReasoningQuestion;
  open: boolean;
  onToggle: () => void;
}

export function TraceDrawer({ question, open, onToggle }: Props) {
  const result = question.dialectica;

  return (
    <section className="sticky bottom-0 z-20 border-t border-border bg-background/95 backdrop-blur">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
        aria-expanded={open}
      >
        <span>
          <span className="text-xs font-semibold uppercase tracking-wide text-accent">Move C</span>
          <span className="ml-2 text-sm font-semibold text-text-primary">Reasoning Trace</span>
        </span>
        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
      </button>
      {open && (
        <div className="grid max-h-[430px] gap-4 overflow-y-auto border-t border-border p-4 lg:grid-cols-4">
          <div className="rounded-lg border border-border bg-surface p-3">
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
              <Network className="h-4 w-4 text-accent" aria-hidden="true" />
              Retrieved subgraph
            </div>
            <p className="text-xs leading-5 text-text-secondary">
              {result.cited_node_ids.length} nodes and {result.cited_edge_ids.length} edges were retrieved by GraphRAG before synthesis.
            </p>
            <pre className="mt-3 overflow-x-auto rounded-md bg-background p-2 text-[11px] text-text-secondary">
              {JSON.stringify({ nodes: result.cited_node_ids, edges: result.cited_edge_ids }, null, 2)}
            </pre>
          </div>
          <div className="rounded-lg border border-border bg-surface p-3">
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
              <Code2 className="h-4 w-4 text-accent" aria-hidden="true" />
              Cypher
            </div>
            <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-md bg-background p-2 text-[11px] leading-5 text-text-secondary">
              {result.cypher_queries.join("\n\n")}
            </pre>
          </div>
          <div className="rounded-lg border border-border bg-surface p-3">
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
              <Sigma className="h-4 w-4 text-accent" aria-hidden="true" />
              Symbolic
            </div>
            <ul className="space-y-2 text-xs text-text-secondary">
              {result.symbolic_rules_fired.map((rule) => (
                <li key={rule} className="rounded-md bg-background px-2 py-1 font-mono">
                  {rule}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-lg border border-border bg-surface p-3">
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
              <SquareCode className="h-4 w-4 text-accent" aria-hidden="true" />
              Result JSON
            </div>
            <pre className="max-h-64 overflow-auto rounded-md bg-background p-2 text-[11px] leading-5 text-text-secondary">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </section>
  );
}
