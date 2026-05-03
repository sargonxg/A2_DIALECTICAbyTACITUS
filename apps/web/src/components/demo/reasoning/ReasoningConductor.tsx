"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowLeft, ExternalLink, FlaskConical, GitBranch, Network } from "lucide-react";
import ForceGraph from "@/components/graph/ForceGraph";
import type { GraphData } from "@/types/graph";
import { AnswerComparison } from "./AnswerComparison";
import { CounterfactualToggler } from "./CounterfactualToggler";
import { getReasoningScenario, cloneGraph } from "./reasoningData";
import { PathHighlightOverlay } from "./PathHighlightOverlay";
import { QuestionLibrary } from "./QuestionLibrary";
import { SimilarityPanel } from "./SimilarityPanel";
import { TraceDrawer } from "./TraceDrawer";

interface Props {
  scenarioId: string;
}

function useContainerWidth() {
  const ref = useRef<HTMLDivElement | null>(null);
  const [width, setWidth] = useState(720);

  useEffect(() => {
    if (!ref.current) return;
    const observer = new ResizeObserver(([entry]) => {
      setWidth(Math.max(320, Math.floor(entry.contentRect.width)));
    });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return { ref, width };
}

function ReasoningGraph({
  graph,
  highlightedNodeIds,
  highlightedEdgeIds,
}: {
  graph: GraphData;
  highlightedNodeIds: string[];
  highlightedEdgeIds: string[];
}) {
  const { ref, width } = useContainerWidth();
  const data = useMemo(() => cloneGraph(graph), [graph]);

  return (
    <div ref={ref} className="min-h-[360px] rounded-lg border border-border bg-surface p-2">
      <ForceGraph
        data={data}
        width={width - 16}
        height={360}
        highlightNodeIds={highlightedNodeIds}
        highlightEdgeIds={highlightedEdgeIds}
      />
    </div>
  );
}

export function ReasoningConductor({ scenarioId }: Props) {
  const scenario = getReasoningScenario(scenarioId);
  const [activeId, setActiveId] = useState(scenario?.questions[0]?.id ?? "");
  const [traceOpen, setTraceOpen] = useState(false);
  const [counterfactualActive, setCounterfactualActive] = useState(false);

  useEffect(() => {
    if (scenario?.questions[0]?.id) setActiveId(scenario.questions[0].id);
  }, [scenario?.id]);

  if (!scenario) {
    return (
      <main className="min-h-screen bg-background p-6">
        <section className="mx-auto max-w-3xl rounded-lg border border-border bg-surface p-6">
          <p className="text-xs font-semibold uppercase tracking-wide text-danger">Unknown scenario</p>
          <h1 className="mt-2 text-3xl font-semibold text-text-primary">No reasoning library found.</h1>
          <Link href="/demo" className="btn-primary mt-6 inline-flex">
            Back to demo
          </Link>
        </section>
      </main>
    );
  }

  const activeQuestion =
    scenario.questions.find((question) => question.id === activeId) ?? scenario.questions[0];
  const highlightedNodeIds = counterfactualActive
    ? activeQuestion.dialectica.cited_node_ids.filter(
        (id) => !activeQuestion.counterfactual?.removed_node_ids.includes(id)
      )
    : activeQuestion.dialectica.cited_node_ids;
  const highlightedEdgeIds = counterfactualActive
    ? activeQuestion.dialectica.cited_edge_ids.filter(
        (id) => !activeQuestion.counterfactual?.removed_edge_ids.includes(id)
      )
    : activeQuestion.dialectica.cited_edge_ids;

  return (
    <main className="flex min-h-screen flex-col bg-background text-text-primary">
      <header className="border-b border-border bg-background/95 px-4 py-3 backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex flex-wrap items-center gap-2 text-xs text-text-secondary">
              <Link href="/demo" className="inline-flex items-center gap-1 hover:text-text-primary">
                <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
                Extraction theatre
              </Link>
              <span>/</span>
              <span>{scenario.workspace_id}</span>
            </div>
            <h1 className="mt-1 text-2xl font-semibold text-text-primary">{scenario.title} reasoning theatre</h1>
            <p className="text-sm text-text-secondary">{scenario.subtitle}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/admin/architecture" className="btn-secondary inline-flex items-center gap-2" target="_blank" rel="noreferrer">
              Architecture
              <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
            </Link>
            <Link href="/demo" className="btn-primary inline-flex items-center gap-2">
              Try another graph
            </Link>
          </div>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <QuestionLibrary
          questions={scenario.questions}
          activeId={activeQuestion.id}
          onSelect={(id) => {
            setActiveId(id);
            setCounterfactualActive(false);
          }}
        />
        <section className="min-w-0 flex-1 overflow-y-auto">
          <div className="space-y-4 p-4">
            <section className="rounded-lg border border-border bg-surface p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-mono text-xs font-semibold text-accent">{activeQuestion.id}</p>
                  <h2 className="mt-1 max-w-4xl text-2xl font-semibold leading-8 text-text-primary">
                    {activeQuestion.text}
                  </h2>
                  <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">{activeQuestion.stake}</p>
                </div>
                <div className="rounded-md border border-border bg-background px-3 py-2 text-xs text-text-secondary">
                  <span className="block font-semibold text-text-primary">{activeQuestion.primary_framework}</span>
                  {activeQuestion.academic_anchor}
                </div>
              </div>
            </section>

            <AnswerComparison
              question={activeQuestion}
              counterfactualActive={counterfactualActive}
              onTraceOpen={() => setTraceOpen(true)}
            />

            <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-text-primary">
                  <Network className="h-4 w-4 text-accent" aria-hidden="true" />
                  Workspace graph with cited path highlighted
                </div>
                <ReasoningGraph
                  graph={scenario.graph}
                  highlightedNodeIds={highlightedNodeIds}
                  highlightedEdgeIds={highlightedEdgeIds}
                />
                <PathHighlightOverlay question={activeQuestion} graph={scenario.graph} />
              </div>
              <div className="space-y-3">
                <CounterfactualToggler
                  question={activeQuestion}
                  active={counterfactualActive}
                  onToggle={() => setCounterfactualActive((value) => !value)}
                />
                <SimilarityPanel question={activeQuestion} />
                <div className="rounded-lg border border-border bg-surface p-3">
                  <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
                    <FlaskConical className="h-4 w-4 text-accent" aria-hidden="true" />
                    API contract
                  </div>
                  <p className="text-xs leading-5 text-text-secondary">
                    This first Prompt 2 slice renders deterministic fixtures in the exact result shape expected from
                    <code className="mx-1 rounded bg-background px-1 py-0.5">/reason/curated</code>.
                    The next backend pass wires these cards to <code className="mx-1 rounded bg-background px-1 py-0.5">query_engine.answer</code>.
                  </p>
                </div>
              </div>
            </section>
          </div>
        </section>
      </div>
      <TraceDrawer question={activeQuestion} open={traceOpen} onToggle={() => setTraceOpen((value) => !value)} />
    </main>
  );
}
