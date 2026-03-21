"use client";

import { useState, useMemo, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import * as Tabs from "@radix-ui/react-tabs";
import {
  ArrowLeft,
  Network,
  Users,
  Clock,
  Brain,
  MessageSquare,
  Send,
  Play,
  Filter,
  AlertTriangle,
  WifiOff,
} from "lucide-react";

import { useWorkspaceDetail } from "@/hooks/useApi";
import { useGraphData, useEntities } from "@/hooks/useGraph";
import { api } from "@/lib/api";
import {
  cn,
  capitalize,
  formatDate,
  glaslLevel,
  GLASL_COLORS,
  NODE_COLORS,
} from "@/lib/utils";
import ForceGraph from "@/components/graph/ForceGraph";
import GlaslStageIndicator from "@/components/analysis/GlaslStageIndicator";
import KriesbergPhaseTracker from "@/components/analysis/KriesbergPhaseTracker";
import type { GraphNode } from "@/types/graph";
import type { AnalysisMode } from "@/types/api";

/* ---------- Tab definitions ---------- */
const TAB_ITEMS = [
  { value: "graph", label: "Graph", icon: Network },
  { value: "entities", label: "Entities", icon: Users },
  { value: "timeline", label: "Timeline", icon: Clock },
  { value: "analysis", label: "Analysis", icon: Brain },
  { value: "query", label: "Query", icon: MessageSquare },
] as const;

/* ====================================================================
   Main Page
   ==================================================================== */
export default function WorkspaceDetailPage() {
  const { id } = useParams();
  const workspaceId = id as string;

  const {
    data: workspace,
    isLoading: wsLoading,
    isError: wsError,
  } = useWorkspaceDetail(workspaceId);

  /* ---- Loading skeleton ---- */
  if (wsLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="h-8 w-64 rounded bg-surface-hover animate-pulse" />
        <div className="flex gap-2">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-6 w-20 rounded bg-surface-hover animate-pulse"
            />
          ))}
        </div>
        <div className="h-[500px] rounded-lg bg-surface-hover animate-pulse" />
      </div>
    );
  }

  /* ---- Error / offline ---- */
  if (wsError || !workspace) {
    return (
      <div className="p-6 space-y-4">
        <Link
          href="/workspaces"
          className="btn-ghost inline-flex items-center gap-1"
        >
          <ArrowLeft size={16} /> Back
        </Link>
        <div className="card text-center py-16">
          <WifiOff size={32} className="mx-auto text-text-secondary mb-3" />
          <p className="text-text-secondary">
            Unable to load workspace. The API may be offline.
          </p>
          <Link href="/workspaces" className="btn-primary mt-4 inline-block">
            Return to Workspaces
          </Link>
        </div>
      </div>
    );
  }

  const glaslLvl = workspace.glasl_stage
    ? glaslLevel(workspace.glasl_stage)
    : null;

  return (
    <div className="p-6 space-y-6">
      {/* ---- Top bar ---- */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/workspaces"
            className="btn-ghost p-2 rounded-md"
            aria-label="Back to workspaces"
          >
            <ArrowLeft size={18} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              {workspace.name}
            </h1>
            {workspace.description && (
              <p className="text-sm text-text-secondary mt-0.5">
                {workspace.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Domain badge */}
          <span className="badge bg-accent/15 text-accent">
            {capitalize(workspace.domain)}
          </span>

          {/* Glasl badge */}
          {workspace.glasl_stage != null && glaslLvl && (
            <span
              className="badge"
              style={{
                backgroundColor: GLASL_COLORS[glaslLvl] + "25",
                color: GLASL_COLORS[glaslLvl],
              }}
            >
              <AlertTriangle size={12} className="mr-1" />
              Glasl {workspace.glasl_stage}
            </span>
          )}

          {/* Tier badge */}
          <span className="badge bg-surface-hover text-text-secondary">
            {capitalize(workspace.tier)}
          </span>

          {/* Scale badge */}
          <span className="badge bg-surface-hover text-text-secondary">
            {capitalize(workspace.scale)}
          </span>
        </div>
      </div>

      {/* ---- Tabs ---- */}
      <Tabs.Root defaultValue="graph">
        <Tabs.List className="flex border-b border-border gap-1 mb-6">
          {TAB_ITEMS.map(({ value, label, icon: Icon }) => (
            <Tabs.Trigger
              key={value}
              value={value}
              className={cn(
                "flex items-center gap-1.5 px-4 py-2 text-sm font-medium transition-colors",
                "border-b-2 border-transparent -mb-px",
                "text-text-secondary hover:text-text-primary",
                "data-[state=active]:border-accent data-[state=active]:text-accent",
              )}
            >
              <Icon size={15} />
              {label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        {/* Tab 1: Graph */}
        <Tabs.Content value="graph">
          <GraphTab workspaceId={workspaceId} workspace={workspace} />
        </Tabs.Content>

        {/* Tab 2: Entities */}
        <Tabs.Content value="entities">
          <EntitiesTab workspaceId={workspaceId} />
        </Tabs.Content>

        {/* Tab 3: Timeline */}
        <Tabs.Content value="timeline">
          <TimelineTab workspaceId={workspaceId} />
        </Tabs.Content>

        {/* Tab 4: Analysis */}
        <Tabs.Content value="analysis">
          <AnalysisTab workspaceId={workspaceId} workspace={workspace} />
        </Tabs.Content>

        {/* Tab 5: Query */}
        <Tabs.Content value="query">
          <QueryTab workspaceId={workspaceId} />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
}

/* ====================================================================
   Tab 1 — Graph
   ==================================================================== */
function GraphTab({
  workspaceId,
  workspace,
}: {
  workspaceId: string;
  workspace: { node_count: number; edge_count: number };
}) {
  const { data: graph, isLoading, isError } = useGraphData(workspaceId);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  /* Compute quick stats from actual graph data */
  const typeBreakdown = useMemo(() => {
    if (!graph?.nodes) return {};
    const counts: Record<string, number> = {};
    for (const n of graph.nodes) {
      counts[n.node_type] = (counts[n.node_type] || 0) + 1;
    }
    return counts;
  }, [graph]);

  if (isLoading) {
    return (
      <div className="h-[500px] rounded-lg bg-surface-hover animate-pulse" />
    );
  }

  if (isError || !graph) {
    return (
      <div className="card text-center py-16">
        <WifiOff size={28} className="mx-auto text-text-secondary mb-3" />
        <p className="text-text-secondary">
          Connect API to view the conflict graph
        </p>
      </div>
    );
  }

  if (graph.nodes.length === 0) {
    return (
      <div className="card text-center py-16">
        <Network size={28} className="mx-auto text-text-secondary mb-3" />
        <p className="text-text-secondary">
          No graph data yet. Ingest documents to populate the graph.
        </p>
        <Link
          href={`/workspaces/${workspaceId}/ingest`}
          className="btn-primary mt-4 inline-block"
        >
          Ingest Documents
        </Link>
      </div>
    );
  }

  return (
    <div className="flex gap-4">
      {/* Graph area */}
      <div className="flex-1 card p-0 overflow-hidden">
        <ForceGraph
          data={graph}
          width={900}
          height={560}
          selectedNodeId={selectedNode?.id ?? null}
          onNodeClick={(node) => setSelectedNode(node)}
        />
      </div>

      {/* Right sidebar */}
      <div className="w-64 space-y-4 flex-shrink-0">
        {/* Quick stats */}
        <div className="card space-y-3">
          <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Quick Stats
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">Nodes</span>
              <span className="text-text-primary font-mono">
                {graph.nodes.length}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">Edges</span>
              <span className="text-text-primary font-mono">
                {graph.links.length}
              </span>
            </div>
          </div>
        </div>

        {/* Type breakdown */}
        <div className="card space-y-3">
          <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Node Types
          </h3>
          <div className="space-y-1.5">
            {Object.entries(typeBreakdown)
              .sort(([, a], [, b]) => b - a)
              .map(([type, count]) => (
                <div key={type} className="flex items-center gap-2 text-sm">
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{
                      backgroundColor: NODE_COLORS[type] || "#94a3b8",
                    }}
                  />
                  <span className="text-text-secondary flex-1">
                    {capitalize(type.replace("_", " "))}
                  </span>
                  <span className="text-text-primary font-mono text-xs">
                    {count}
                  </span>
                </div>
              ))}
          </div>
        </div>

        {/* Selected node detail */}
        {selectedNode && (
          <div className="card space-y-2">
            <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Selected Node
            </h3>
            <p className="text-text-primary font-medium">{selectedNode.name}</p>
            <div className="flex items-center gap-2 text-xs">
              <span
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor:
                    NODE_COLORS[selectedNode.node_type] || "#94a3b8",
                }}
              />
              <span className="text-text-secondary">
                {capitalize(selectedNode.node_type.replace("_", " "))}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-text-secondary">Confidence</span>
              <span className="text-text-primary font-mono">
                {(selectedNode.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ====================================================================
   Tab 2 — Entities
   ==================================================================== */
const ALL_NODE_TYPES = [
  "actor",
  "conflict",
  "event",
  "issue",
  "interest",
  "norm",
  "process",
  "outcome",
  "narrative",
  "emotional_state",
  "trust_state",
  "power_dynamic",
  "location",
  "evidence",
  "role",
] as const;

function EntitiesTab({ workspaceId }: { workspaceId: string }) {
  const [typeFilter, setTypeFilter] = useState<string>("");
  const {
    data: entities,
    isLoading,
    isError,
  } = useEntities(workspaceId, typeFilter || undefined);

  if (isError) {
    return (
      <div className="card text-center py-16">
        <WifiOff size={28} className="mx-auto text-text-secondary mb-3" />
        <p className="text-text-secondary">
          Connect API to view entities
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter bar */}
      <div className="flex items-center gap-3">
        <Filter size={16} className="text-text-secondary" />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="input-base"
        >
          <option value="">All types</option>
          {ALL_NODE_TYPES.map((t) => (
            <option key={t} value={t}>
              {capitalize(t.replace("_", " "))}
            </option>
          ))}
        </select>
        {entities && (
          <span className="text-xs text-text-secondary">
            {entities.total} entit{entities.total === 1 ? "y" : "ies"}
          </span>
        )}
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="h-12 rounded bg-surface-hover animate-pulse"
            />
          ))}
        </div>
      ) : !entities || entities.items.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-text-secondary">
            {typeFilter
              ? `No ${capitalize(typeFilter.replace("_", " "))} entities found`
              : "No entities in this workspace yet"}
          </p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface-hover/50">
                <th className="text-left px-4 py-3 text-text-secondary font-medium">
                  Name
                </th>
                <th className="text-left px-4 py-3 text-text-secondary font-medium">
                  Type
                </th>
                <th className="text-right px-4 py-3 text-text-secondary font-medium">
                  Confidence
                </th>
              </tr>
            </thead>
            <tbody>
              {entities.items.map((entity, idx) => {
                const name =
                  (entity.name as string) ||
                  (entity.label as string) ||
                  (entity.id as string) ||
                  "Unknown";
                const nodeType = (entity.node_type as string) || (entity.label as string) || "";
                const confidence = (entity.confidence as number) ?? 0;
                return (
                  <tr
                    key={(entity.id as string) || idx}
                    className="border-b border-border last:border-0 hover:bg-surface-hover transition-colors"
                  >
                    <td className="px-4 py-3 text-text-primary font-medium">
                      {name}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center gap-1.5">
                        <span
                          className="w-2 h-2 rounded-full"
                          style={{
                            backgroundColor:
                              NODE_COLORS[nodeType] || "#94a3b8",
                          }}
                        />
                        <span className="text-text-secondary">
                          {capitalize(nodeType.replace("_", " ") || "unknown")}
                        </span>
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-text-secondary">
                      {(confidence * 100).toFixed(0)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ====================================================================
   Tab 3 — Timeline
   ==================================================================== */
function TimelineTab({ workspaceId }: { workspaceId: string }) {
  const {
    data: entities,
    isLoading,
    isError,
  } = useEntities(workspaceId, "event");

  if (isError) {
    return (
      <div className="card text-center py-16">
        <WifiOff size={28} className="mx-auto text-text-secondary mb-3" />
        <p className="text-text-secondary">
          Connect API to view timeline events
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="card h-20 animate-pulse bg-surface-hover"
          />
        ))}
      </div>
    );
  }

  /* Sort events by date descending, fall back to created_at */
  const events = (entities?.items ?? [])
    .map((e) => ({
      id: e.id as string,
      name: (e.name as string) || "Unnamed event",
      occurred_at: (e.occurred_at as string) || (e.created_at as string) || "",
      event_type: (e.event_type as string) || "event",
      severity: (e.severity as number) ?? 0.5,
      description: (e.description as string) || "",
    }))
    .sort((a, b) => {
      if (!a.occurred_at) return 1;
      if (!b.occurred_at) return -1;
      return (
        new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
      );
    });

  if (events.length === 0) {
    return (
      <div className="card text-center py-16">
        <Clock size={28} className="mx-auto text-text-secondary mb-3" />
        <p className="text-text-secondary">
          No timeline events recorded yet
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <div key={event.id} className="card flex items-start gap-4">
          {/* Date column */}
          <div className="flex-shrink-0 w-24 text-right">
            {event.occurred_at ? (
              <p className="text-sm text-text-primary font-mono">
                {formatDate(event.occurred_at)}
              </p>
            ) : (
              <p className="text-xs text-text-secondary italic">No date</p>
            )}
          </div>

          {/* Divider dot */}
          <div className="flex flex-col items-center pt-1.5">
            <span
              className="w-3 h-3 rounded-full"
              style={{
                backgroundColor:
                  NODE_COLORS[event.event_type] || "#eab308",
              }}
            />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-text-primary font-medium text-sm">
                {event.name}
              </span>
              <span
                className="badge text-[10px]"
                style={{
                  backgroundColor:
                    (NODE_COLORS[event.event_type] || "#eab308") + "20",
                  color: NODE_COLORS[event.event_type] || "#eab308",
                }}
              >
                {capitalize(event.event_type.replace("_", " "))}
              </span>
            </div>
            {event.description && (
              <p className="text-xs text-text-secondary line-clamp-2">
                {event.description}
              </p>
            )}
          </div>

          {/* Severity indicator */}
          <div className="flex-shrink-0 text-right">
            <span
              className={cn(
                "text-xs font-mono",
                event.severity > 0.7
                  ? "text-danger"
                  : event.severity > 0.4
                    ? "text-warning"
                    : "text-text-secondary",
              )}
            >
              {(event.severity * 10).toFixed(1)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ====================================================================
   Tab 4 — Analysis
   ==================================================================== */
function AnalysisTab({
  workspaceId,
  workspace,
}: {
  workspaceId: string;
  workspace: {
    node_count: number;
    edge_count: number;
    glasl_stage?: number;
    kriesberg_phase?: string;
    domain: string;
    scale: string;
    tier: string;
  };
}) {
  const [isRunning, setIsRunning] = useState(false);

  return (
    <div className="space-y-6">
      {/* Glasl + Kriesberg panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {workspace.glasl_stage && (
          <GlaslStageIndicator currentStage={workspace.glasl_stage} />
        )}
        <KriesbergPhaseTracker
          currentPhase={
            workspace.kriesberg_phase as
              | "emergence"
              | "escalation"
              | "de_escalation"
              | "settlement"
              | "post_settlement"
              | undefined
          }
        />
      </div>

      {/* Quick stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <p className="text-2xl font-mono font-bold text-text-primary">
            {workspace.node_count}
          </p>
          <p className="text-xs text-text-secondary mt-1">Nodes</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-mono font-bold text-text-primary">
            {workspace.edge_count}
          </p>
          <p className="text-xs text-text-secondary mt-1">Edges</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-mono font-bold text-accent">
            {capitalize(workspace.domain)}
          </p>
          <p className="text-xs text-text-secondary mt-1">Domain</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-mono font-bold text-text-primary">
            {capitalize(workspace.tier)}
          </p>
          <p className="text-xs text-text-secondary mt-1">Ontology Tier</p>
        </div>
      </div>

      {/* Run Analysis placeholder */}
      <div className="card">
        <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
          Run Analysis
        </h3>
        <p className="text-sm text-text-secondary mb-4">
          Run a full conflict analysis using DIALECTICA&apos;s symbolic reasoning
          engine and AI agents. This will evaluate escalation dynamics, power
          structures, trust states, and narrative patterns.
        </p>
        <button
          className="btn-primary inline-flex items-center gap-2"
          disabled={isRunning}
          onClick={() => {
            setIsRunning(true);
            /* Placeholder -- will integrate with api.analyze in the future */
            setTimeout(() => setIsRunning(false), 2000);
          }}
        >
          <Play size={14} />
          {isRunning ? "Running..." : "Run Analysis"}
        </button>
      </div>
    </div>
  );
}

/* ====================================================================
   Tab 5 — Query
   ==================================================================== */
function QueryTab({ workspaceId }: { workspaceId: string }) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<AnalysisMode>("general");
  const [response, setResponse] = useState<string | null>(null);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = useCallback(async () => {
    if (!query.trim()) return;
    setIsAsking(true);
    setError(null);
    setResponse(null);

    try {
      const result = await api.analyze({
        workspace_id: workspaceId,
        query: query.trim(),
        mode,
        include_theory: true,
      });
      setResponse(result.assessment);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to get a response. Please try again.",
      );
    } finally {
      setIsAsking(false);
    }
  }, [query, mode, workspaceId]);

  return (
    <div className="max-w-3xl space-y-4">
      {/* Mode selector */}
      <div className="flex items-center gap-3">
        <label className="text-sm text-text-secondary">Mode:</label>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value as AnalysisMode)}
          className="input-base"
        >
          <option value="general">General</option>
          <option value="escalation">Escalation</option>
          <option value="ripeness">Ripeness</option>
          <option value="trust">Trust</option>
          <option value="power">Power</option>
          <option value="causal">Causal</option>
          <option value="narrative">Narrative</option>
        </select>
      </div>

      {/* Query input */}
      <div className="card space-y-3">
        <label className="text-sm font-medium text-text-secondary block">
          Ask a question about this conflict
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., What are the main escalation drivers? Who holds the most leverage?"
          rows={4}
          className="input-base w-full resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              handleAsk();
            }
          }}
        />
        <div className="flex items-center justify-between">
          <p className="text-[11px] text-text-secondary">
            Ctrl+Enter to send
          </p>
          <button
            className="btn-primary inline-flex items-center gap-2"
            onClick={handleAsk}
            disabled={isAsking || !query.trim()}
          >
            <Send size={14} />
            {isAsking ? "Thinking..." : "Ask"}
          </button>
        </div>
      </div>

      {/* Response area */}
      {error && (
        <div className="card border-danger/30 bg-danger/5">
          <p className="text-sm text-danger">{error}</p>
        </div>
      )}

      {response && (
        <div className="card">
          <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-2">
            Response
          </h3>
          <div className="text-sm text-text-primary whitespace-pre-wrap leading-relaxed">
            {response}
          </div>
        </div>
      )}

      {!response && !error && !isAsking && (
        <div className="card text-center py-12">
          <MessageSquare
            size={28}
            className="mx-auto text-text-secondary mb-3"
          />
          <p className="text-text-secondary text-sm">
            Ask a question to analyze this conflict using DIALECTICA&apos;s
            reasoning engine
          </p>
        </div>
      )}

      {isAsking && (
        <div className="card text-center py-12">
          <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-text-secondary text-sm">
            Analyzing conflict data...
          </p>
        </div>
      )}
    </div>
  );
}
