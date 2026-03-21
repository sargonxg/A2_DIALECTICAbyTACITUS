"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import {
  Users,
  Globe,
  Briefcase,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Network,
  ArrowRight,
} from "lucide-react";
import ForceGraph from "@/components/graph/ForceGraph";
import { NODE_COLORS } from "@/lib/utils";
import { SAMPLES } from "@/data/sample-texts";
import type { GraphData, GraphNode, GraphLink } from "@/types/graph";
import type { NodeType } from "@/types/ontology";

/* ------------------------------------------------------------------ */
/*  Fallback data derived from hr_mediation.json seed file             */
/* ------------------------------------------------------------------ */

const FALLBACK_NODES: GraphNode[] = [
  {
    id: "actor_alex",
    label: "Actor",
    node_type: "actor",
    name: "Alex Chen",
    confidence: 0.95,
    properties: { role_title: "Software Developer", actor_type: "person", centrality: 0.7 },
  },
  {
    id: "actor_maya",
    label: "Actor",
    node_type: "actor",
    name: "Maya Okonkwo",
    confidence: 0.95,
    properties: { role_title: "Senior Developer / Team Lead", actor_type: "person", centrality: 0.75 },
  },
  {
    id: "actor_jordan",
    label: "Actor",
    node_type: "actor",
    name: "Jordan Reyes",
    confidence: 0.9,
    properties: { role_title: "HR Business Partner / Mediator", actor_type: "person", centrality: 0.5 },
  },
  {
    id: "conflict_code_review",
    label: "Conflict",
    node_type: "conflict",
    name: "Code Review Incident",
    confidence: 0.95,
    properties: { glasl_stage: 3, status: "active", scale: "micro", domain: "workplace", centrality: 1.0 },
  },
  {
    id: "event_code_review_incident",
    label: "Event",
    node_type: "event",
    name: "Public Code Review",
    confidence: 0.92,
    properties: { event_type: "disapprove", severity: 0.55, occurred_at: "2025-11-14", centrality: 0.65 },
  },
  {
    id: "event_formal_complaint",
    label: "Event",
    node_type: "event",
    name: "Formal HR Complaint",
    confidence: 0.9,
    properties: { event_type: "demand", severity: 0.45, occurred_at: "2025-11-21", centrality: 0.6 },
  },
  {
    id: "event_mediation_session",
    label: "Event",
    node_type: "event",
    name: "Mediation Session",
    confidence: 0.88,
    properties: { event_type: "consult", severity: 0.2, occurred_at: "2025-12-05", centrality: 0.55 },
  },
  {
    id: "issue_communication_style",
    label: "Issue",
    node_type: "issue",
    name: "Communication Style",
    confidence: 0.9,
    properties: { issue_type: "procedural", salience: 0.85, centrality: 0.6 },
  },
  {
    id: "issue_professional_respect",
    label: "Issue",
    node_type: "issue",
    name: "Professional Respect",
    confidence: 0.92,
    properties: { issue_type: "psychological", salience: 0.9, centrality: 0.65 },
  },
  {
    id: "process_hr_mediation",
    label: "Process",
    node_type: "process",
    name: "HR Mediation",
    confidence: 0.88,
    properties: { process_type: "mediation_facilitative", status: "active", centrality: 0.55 },
  },
  {
    id: "interest_dignity",
    label: "Interest",
    node_type: "interest",
    name: "Professional Dignity",
    confidence: 0.85,
    properties: { holder: "Alex Chen", importance: "high", centrality: 0.45 },
  },
  {
    id: "interest_code_quality",
    label: "Interest",
    node_type: "interest",
    name: "Code Quality Standards",
    confidence: 0.88,
    properties: { holder: "Alex Chen", importance: "high", centrality: 0.5 },
  },
  {
    id: "interest_team_velocity",
    label: "Interest",
    node_type: "interest",
    name: "Team Velocity",
    confidence: 0.85,
    properties: { holder: "Maya Okonkwo", importance: "high", centrality: 0.45 },
  },
  {
    id: "norm_code_of_conduct",
    label: "Norm",
    node_type: "norm",
    name: "Company Code of Conduct",
    confidence: 0.9,
    properties: { norm_type: "organizational_policy", centrality: 0.4 },
  },
  {
    id: "emotional_alex_humiliation",
    label: "Emotional State",
    node_type: "emotional_state",
    name: "Humiliation & Distrust",
    confidence: 0.82,
    properties: { holder: "Alex Chen", valence: "negative", intensity: 0.8, centrality: 0.35 },
  },
  {
    id: "trust_breakdown",
    label: "Trust State",
    node_type: "trust_state",
    name: "Trust Breakdown",
    confidence: 0.85,
    properties: { between: "Alex ↔ Maya", level: "low", direction: "deteriorating", centrality: 0.5 },
  },
  {
    id: "power_seniority",
    label: "Power Dynamic",
    node_type: "power_dynamic",
    name: "Positional Power",
    confidence: 0.88,
    properties: { domain: "positional", magnitude: 0.6, direction: "Maya over Alex", centrality: 0.4 },
  },
];

const FALLBACK_LINKS: GraphLink[] = [
  { id: "e1", source: "actor_alex", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.9, confidence: 0.95 },
  { id: "e2", source: "actor_maya", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.9, confidence: 0.95 },
  { id: "e3", source: "actor_jordan", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.7, confidence: 0.9 },
  { id: "e4", source: "event_code_review_incident", target: "event_formal_complaint", edge_type: "CAUSED", weight: 0.85, confidence: 0.95 },
  { id: "e5", source: "event_formal_complaint", target: "event_mediation_session", edge_type: "CAUSED", weight: 0.8, confidence: 0.9 },
  { id: "e6", source: "issue_communication_style", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.85, confidence: 0.9 },
  { id: "e7", source: "issue_professional_respect", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.9, confidence: 0.92 },
  { id: "e8", source: "actor_alex", target: "process_hr_mediation", edge_type: "PARTICIPATES_IN", weight: 0.7, confidence: 0.88 },
  { id: "e9", source: "actor_maya", target: "process_hr_mediation", edge_type: "PARTICIPATES_IN", weight: 0.7, confidence: 0.88 },
  { id: "e10", source: "actor_jordan", target: "process_hr_mediation", edge_type: "PARTICIPATES_IN", weight: 0.8, confidence: 0.9 },
  { id: "e11", source: "conflict_code_review", target: "process_hr_mediation", edge_type: "RESOLVED_THROUGH", weight: 0.75, confidence: 0.85 },
  { id: "e12", source: "actor_maya", target: "actor_alex", edge_type: "HAS_POWER_OVER", weight: 0.6, confidence: 0.88 },
  { id: "e13", source: "actor_alex", target: "interest_dignity", edge_type: "HAS_INTEREST", weight: 0.85, confidence: 0.85 },
  { id: "e14", source: "actor_alex", target: "interest_code_quality", edge_type: "HAS_INTEREST", weight: 0.8, confidence: 0.88 },
  { id: "e15", source: "actor_maya", target: "interest_team_velocity", edge_type: "HAS_INTEREST", weight: 0.8, confidence: 0.85 },
  { id: "e16", source: "actor_maya", target: "event_code_review_incident", edge_type: "PERFORMED", weight: 0.9, confidence: 0.92 },
  { id: "e17", source: "event_code_review_incident", target: "actor_alex", edge_type: "TARGETED", weight: 0.85, confidence: 0.9 },
  { id: "e18", source: "norm_code_of_conduct", target: "conflict_code_review", edge_type: "GOVERNS", weight: 0.7, confidence: 0.9 },
  { id: "e19", source: "actor_alex", target: "emotional_alex_humiliation", edge_type: "EXPERIENCES", weight: 0.75, confidence: 0.82 },
  { id: "e20", source: "actor_alex", target: "trust_breakdown", edge_type: "HAS_TRUST_STATE", weight: 0.8, confidence: 0.85 },
  { id: "e21", source: "actor_maya", target: "trust_breakdown", edge_type: "HAS_TRUST_STATE", weight: 0.8, confidence: 0.85 },
  { id: "e22", source: "power_seniority", target: "actor_maya", edge_type: "HELD_BY", weight: 0.6, confidence: 0.88 },
  { id: "e23", source: "emotional_alex_humiliation", target: "event_formal_complaint", edge_type: "MOTIVATED", weight: 0.7, confidence: 0.8 },
];

const FALLBACK_GRAPH: GraphData = {
  nodes: FALLBACK_NODES,
  links: FALLBACK_LINKS,
};

/* ------------------------------------------------------------------ */
/*  Icons for sample buttons                                           */
/* ------------------------------------------------------------------ */

const ICON_MAP: Record<string, React.ElementType> = {
  Users,
  Globe,
  Briefcase,
};

/* ------------------------------------------------------------------ */
/*  Loading step trace                                                 */
/* ------------------------------------------------------------------ */

interface Step {
  label: string;
  status: "pending" | "active" | "done" | "error";
}

const INITIAL_STEPS: Step[] = [
  { label: "Parsing conflict narrative", status: "pending" },
  { label: "Extracting entities (GLiNER + Gemini)", status: "pending" },
  { label: "Building knowledge graph", status: "pending" },
  { label: "Running symbolic inference", status: "pending" },
  { label: "Rendering visualization", status: "pending" },
];

/* ------------------------------------------------------------------ */
/*  Stats helpers                                                      */
/* ------------------------------------------------------------------ */

function computeStats(data: GraphData) {
  const typeCount: Record<string, number> = {};
  for (const node of data.nodes) {
    typeCount[node.node_type] = (typeCount[node.node_type] || 0) + 1;
  }

  const edgeTypeCount: Record<string, number> = {};
  for (const link of data.links) {
    edgeTypeCount[link.edge_type] = (edgeTypeCount[link.edge_type] || 0) + 1;
  }

  const avgConfidence =
    data.nodes.length > 0
      ? data.nodes.reduce((sum, n) => sum + n.confidence, 0) / data.nodes.length
      : 0;

  return { typeCount, edgeTypeCount, avgConfidence };
}

/* ------------------------------------------------------------------ */
/*  Main Demo Page                                                     */
/* ------------------------------------------------------------------ */

export default function DemoPage() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isFallback, setIsFallback] = useState(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const [graphSize, setGraphSize] = useState({ width: 800, height: 600 });
  const resultsRef = useRef<HTMLDivElement>(null);

  /* Responsive graph sizing */
  useEffect(() => {
    function updateSize() {
      if (graphContainerRef.current) {
        const rect = graphContainerRef.current.getBoundingClientRect();
        setGraphSize({
          width: Math.max(400, Math.floor(rect.width)),
          height: Math.max(400, Math.floor(rect.height)),
        });
      }
    }
    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, [graphData]);

  /* Advance loading step trace */
  const advanceStep = useCallback(
    (index: number, status: "active" | "done" | "error") => {
      setSteps((prev) =>
        prev.map((s, i) => {
          if (i === index) return { ...s, status };
          if (i < index && s.status !== "error") return { ...s, status: "done" };
          return s;
        }),
      );
    },
    [],
  );

  /* Simulate step progress (used for both API and fallback paths) */
  const simulateSteps = useCallback(
    async (useFallback: boolean) => {
      const delays = [600, 900, 700, 500, 400];
      for (let i = 0; i < INITIAL_STEPS.length; i++) {
        advanceStep(i, "active");
        await new Promise((r) => setTimeout(r, delays[i]));
        if (i === INITIAL_STEPS.length - 1) {
          advanceStep(i, "done");
        } else if (useFallback && i === 1) {
          /* On fallback, mark extraction as error, then continue with fallback */
          advanceStep(i, "error");
          await new Promise((r) => setTimeout(r, 300));
          /* Continue remaining steps as done */
          for (let j = i + 1; j < INITIAL_STEPS.length; j++) {
            advanceStep(j, "active");
            await new Promise((r) => setTimeout(r, delays[j]));
            advanceStep(j, "done");
          }
          return;
        } else {
          advanceStep(i, "done");
        }
      }
    },
    [advanceStep],
  );

  /* Handle Analyze */
  const handleAnalyze = useCallback(async () => {
    if (!text.trim()) return;
    setLoading(true);
    setGraphData(null);
    setIsFallback(false);
    setSelectedNode(null);
    setSteps(INITIAL_STEPS.map((s) => ({ ...s, status: "pending" })));

    let usedFallback = false;

    try {
      /* Try the real API */
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
      const apiKey =
        typeof window !== "undefined" ? localStorage.getItem("dialectica_api_key") : null;
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-API-Key": apiKey } : {}),
      };

      /* Step 1-2: Parse and extract */
      advanceStep(0, "active");
      await new Promise((r) => setTimeout(r, 500));
      advanceStep(0, "done");
      advanceStep(1, "active");

      const extractRes = await fetch(`${API_URL}/v1/extract`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          workspace_id: "demo",
          text: text.trim(),
          tier: "standard",
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (!extractRes.ok) throw new Error(`API ${extractRes.status}`);

      const extraction = await extractRes.json();
      advanceStep(1, "done");

      /* Step 3: Get graph */
      advanceStep(2, "active");
      await new Promise((r) => setTimeout(r, 400));

      const graphRes = await fetch(
        `${API_URL}/v1/workspaces/${extraction.workspace_id}/graph`,
        { headers },
      );
      if (!graphRes.ok) throw new Error(`Graph API ${graphRes.status}`);
      const graph: GraphData = await graphRes.json();
      advanceStep(2, "done");

      /* Step 4: Symbolic inference */
      advanceStep(3, "active");
      await new Promise((r) => setTimeout(r, 500));
      advanceStep(3, "done");

      /* Step 5: Render */
      advanceStep(4, "active");
      await new Promise((r) => setTimeout(r, 300));
      advanceStep(4, "done");

      setGraphData(graph);
    } catch {
      /* Fallback path */
      usedFallback = true;
      setSteps(INITIAL_STEPS.map((s) => ({ ...s, status: "pending" })));
      await simulateSteps(true);
      setGraphData(FALLBACK_GRAPH);
      setIsFallback(true);
    } finally {
      setLoading(false);
      if (!usedFallback) {
        setIsFallback(false);
      }
      /* Scroll to results */
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    }
  }, [text, advanceStep, simulateSteps]);

  const stats = graphData ? computeStats(graphData) : null;

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* ---- Header ---- */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Network className="text-accent" size={22} />
            <span className="text-lg font-bold tracking-tight">
              <span className="text-accent">DIALECTICA</span>
              <span className="text-text-secondary font-normal text-sm ml-2">by TACITUS</span>
            </span>
          </div>
          <a
            href="/"
            className="text-xs text-text-secondary hover:text-text-primary transition-colors"
          >
            Back to Dashboard
          </a>
        </div>
      </header>

      {/* ---- Hero / Input Section ---- */}
      <section className="pt-24 pb-12 px-6">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
            Paste any conflict.{" "}
            <span className="text-accent">See it as a knowledge graph.</span>
          </h1>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Workplace disputes, geopolitical crises, commercial negotiations
            &mdash; structured in seconds.
          </p>

          {/* Textarea */}
          <div className="relative">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Describe a conflict, dispute, or negotiation scenario..."
              rows={8}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all resize-y min-h-[200px]"
              disabled={loading}
            />
            <div className="absolute bottom-3 right-3 text-xs text-text-secondary/50">
              {text.length > 0 ? `${text.split(/\s+/).filter(Boolean).length} words` : ""}
            </div>
          </div>

          {/* Sample Buttons */}
          <div className="flex flex-wrap justify-center gap-3">
            {Object.entries(SAMPLES).map(([key, sample]) => {
              const Icon = ICON_MAP[sample.icon] || Sparkles;
              return (
                <button
                  key={key}
                  onClick={() => setText(sample.text)}
                  disabled={loading}
                  className="flex items-center gap-2 px-4 py-2 bg-surface border border-border rounded-lg text-sm text-text-secondary hover:text-text-primary hover:border-border-hover hover:bg-surface-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Icon size={14} />
                  {sample.title}
                </button>
              );
            })}
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className="inline-flex items-center gap-2 px-8 py-3 bg-teal-600 hover:bg-teal-500 disabled:bg-teal-600/50 text-white font-semibold rounded-lg text-base transition-all disabled:cursor-not-allowed shadow-lg shadow-teal-600/20 hover:shadow-teal-500/30"
          >
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Analyze
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </section>

      {/* ---- Loading Step Trace ---- */}
      {loading && (
        <section className="px-6 pb-8">
          <div className="max-w-md mx-auto space-y-3">
            {steps.map((step, i) => (
              <div
                key={i}
                className="flex items-center gap-3 text-sm transition-all duration-300"
              >
                {step.status === "pending" && (
                  <div className="w-5 h-5 rounded-full border border-surface-active" />
                )}
                {step.status === "active" && (
                  <Loader2 size={18} className="text-accent animate-spin shrink-0" />
                )}
                {step.status === "done" && (
                  <CheckCircle2 size={18} className="text-green-500 shrink-0" />
                )}
                {step.status === "error" && (
                  <AlertTriangle size={18} className="text-amber-500 shrink-0" />
                )}
                <span
                  className={
                    step.status === "active"
                      ? "text-text-primary"
                      : step.status === "done"
                        ? "text-text-secondary"
                        : step.status === "error"
                          ? "text-amber-400"
                          : "text-text-secondary/50"
                  }
                >
                  {step.label}
                  {step.status === "error" && (
                    <span className="ml-2 text-xs text-amber-400/70">
                      (API offline — using fallback)
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ---- Results Section ---- */}
      {graphData && (
        <section ref={resultsRef} className="px-6 pb-16 animate-fade-in">
          {/* Fallback Banner */}
          {isFallback && (
            <div className="max-w-7xl mx-auto mb-4">
              <div className="flex items-center gap-2 px-4 py-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-sm text-amber-400">
                <AlertTriangle size={16} className="shrink-0" />
                <span>
                  Demo mode &mdash; API offline. Showing sample HR mediation
                  data.
                </span>
              </div>
            </div>
          )}

          <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6">
            {/* Graph (60%) */}
            <div
              ref={graphContainerRef}
              className="lg:w-[60%] w-full bg-surface border border-border rounded-lg overflow-hidden relative"
              style={{ minHeight: 500 }}
            >
              {/* Legend */}
              <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-2">
                {Object.entries(
                  computeStats(graphData).typeCount,
                ).map(([type, count]) => (
                  <span
                    key={type}
                    className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-background/80 backdrop-blur-sm rounded text-[10px] font-medium text-text-secondary border border-border"
                  >
                    <span
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ backgroundColor: NODE_COLORS[type] || "#94a3b8" }}
                    />
                    {type.replace(/_/g, " ")} ({count})
                  </span>
                ))}
              </div>
              <ForceGraph
                data={graphData}
                width={graphSize.width}
                height={graphSize.height}
                onNodeClick={(node) => setSelectedNode(node)}
                selectedNodeId={selectedNode?.id ?? null}
              />
            </div>

            {/* Sidebar (40%) */}
            <div className="lg:w-[40%] w-full space-y-4">
              {/* Quick Stats */}
              <div className="bg-surface border border-border rounded-lg p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
                  <Network size={16} className="text-accent" />
                  Graph Statistics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <StatCard label="Nodes" value={graphData.nodes.length} />
                  <StatCard label="Edges" value={graphData.links.length} />
                  <StatCard
                    label="Avg Confidence"
                    value={`${Math.round((stats?.avgConfidence ?? 0) * 100)}%`}
                  />
                  <StatCard
                    label="Node Types"
                    value={Object.keys(stats?.typeCount ?? {}).length}
                  />
                </div>
              </div>

              {/* Node Type Breakdown */}
              <div className="bg-surface border border-border rounded-lg p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Entity Breakdown
                </h3>
                <div className="space-y-2">
                  {stats &&
                    Object.entries(stats.typeCount)
                      .sort((a, b) => b[1] - a[1])
                      .map(([type, count]) => (
                        <div key={type} className="flex items-center gap-3">
                          <span
                            className="w-2.5 h-2.5 rounded-full shrink-0"
                            style={{
                              backgroundColor:
                                NODE_COLORS[type as NodeType] || "#94a3b8",
                            }}
                          />
                          <span className="text-sm text-text-secondary flex-1 capitalize">
                            {type.replace(/_/g, " ")}
                          </span>
                          <span className="text-sm font-mono text-text-primary">
                            {count}
                          </span>
                          <div className="w-16 h-1.5 bg-surface-active rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${(count / graphData.nodes.length) * 100}%`,
                                backgroundColor:
                                  NODE_COLORS[type as NodeType] || "#94a3b8",
                              }}
                            />
                          </div>
                        </div>
                      ))}
                </div>
              </div>

              {/* Edge Type Breakdown */}
              <div className="bg-surface border border-border rounded-lg p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Relationship Types
                </h3>
                <div className="space-y-1.5">
                  {stats &&
                    Object.entries(stats.edgeTypeCount)
                      .sort((a, b) => b[1] - a[1])
                      .map(([type, count]) => (
                        <div
                          key={type}
                          className="flex items-center justify-between text-sm"
                        >
                          <span className="text-text-secondary font-mono text-xs">
                            {type}
                          </span>
                          <span className="text-text-primary font-mono">
                            {count}
                          </span>
                        </div>
                      ))}
                </div>
              </div>

              {/* Selected Node Detail */}
              {selectedNode && (
                <div className="bg-surface border border-accent/30 rounded-lg p-5 animate-fade-in">
                  <h3 className="text-sm font-semibold text-accent mb-3 flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor:
                          NODE_COLORS[selectedNode.node_type] || "#94a3b8",
                      }}
                    />
                    {selectedNode.name}
                  </h3>
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-text-secondary">Type</dt>
                      <dd className="text-text-primary capitalize">
                        {selectedNode.node_type.replace(/_/g, " ")}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-text-secondary">Confidence</dt>
                      <dd className="text-text-primary">
                        {Math.round(selectedNode.confidence * 100)}%
                      </dd>
                    </div>
                    {Object.entries(selectedNode.properties)
                      .filter(([k]) => k !== "centrality")
                      .map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <dt className="text-text-secondary capitalize">
                            {key.replace(/_/g, " ")}
                          </dt>
                          <dd className="text-text-primary text-right max-w-[60%] truncate">
                            {String(value)}
                          </dd>
                        </div>
                      ))}
                    <div className="flex justify-between">
                      <dt className="text-text-secondary">Connections</dt>
                      <dd className="text-text-primary">
                        {graphData.links.filter(
                          (l) =>
                            (typeof l.source === "string"
                              ? l.source
                              : l.source.id) === selectedNode.id ||
                            (typeof l.target === "string"
                              ? l.target
                              : l.target.id) === selectedNode.id,
                        ).length}
                      </dd>
                    </div>
                  </dl>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ---- Footer ---- */}
      <footer className="border-t border-border py-6 px-6 text-center text-xs text-text-secondary/50">
        DIALECTICA by TACITUS &mdash; The Universal Data Layer for Human Friction
      </footer>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Stat Card component                                                */
/* ------------------------------------------------------------------ */

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="bg-background rounded-lg px-3 py-2.5 border border-border">
      <div className="text-xl font-bold text-text-primary font-mono">
        {value}
      </div>
      <div className="text-xs text-text-secondary mt-0.5">{label}</div>
    </div>
  );
}
