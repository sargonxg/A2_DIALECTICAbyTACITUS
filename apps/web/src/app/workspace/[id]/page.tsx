"use client";

import { useState, useCallback, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Network, Brain, BookOpen, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import GraphEditor from "@/components/GraphEditor";
import ReasoningPanel from "@/components/ReasoningPanel";
import TheoryGrid from "@/components/TheoryGrid";
import { api } from "@/lib/api";
import type {
  GraphNode,
  GraphEdge,
  ReasoningTrace,
  TheoryAssessment,
} from "@/types/api";

/* ── Types ───────────────────────────────────────────────────────────── */

type TabId = "situation" | "reasoning" | "theories";

const TABS: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: "situation", label: "Situation", icon: Network },
  { id: "reasoning", label: "Reasoning", icon: Brain },
  { id: "theories", label: "Theories", icon: BookOpen },
];

/* ── Loading skeleton ────────────────────────────────────────────────── */

function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-pulse rounded bg-zinc-800/60",
        className,
      )}
    />
  );
}

function PageSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-40" />
      <div className="flex gap-2">
        <Skeleton className="h-9 w-24" />
        <Skeleton className="h-9 w-24" />
        <Skeleton className="h-9 w-24" />
      </div>
      <Skeleton className="h-[500px] w-full" />
    </div>
  );
}

/* ── Error banner ────────────────────────────────────────────────────── */

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-red-800 bg-red-950/40 p-4 text-sm text-red-300">
      <AlertTriangle size={16} className="mt-0.5 shrink-0" />
      <span>{message}</span>
    </div>
  );
}

/* ── Main page ───────────────────────────────────────────────────────── */

export default function WorkspaceDashboardPage() {
  const { id } = useParams();
  const workspaceId = id as string;

  const [activeTab, setActiveTab] = useState<TabId>("situation");

  // Situation layer
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [situationLoading, setSituationLoading] = useState(true);
  const [situationError, setSituationError] = useState<string | null>(null);

  // Reasoning layer
  const [traces, setTraces] = useState<ReasoningTrace[]>([]);
  const [reasoningLoading, setReasoningLoading] = useState(false);
  const [reasoningError, setReasoningError] = useState<string | null>(null);

  // Theory layer
  const [assessments, setAssessments] = useState<TheoryAssessment[]>([]);
  const [theoriesLoading, setTheoriesLoading] = useState(false);
  const [theoriesError, setTheoriesError] = useState<string | null>(null);

  // Load situation graph on mount
  useEffect(() => {
    setSituationLoading(true);
    setSituationError(null);
    api.getGraph(workspaceId)
      .then((data) => {
        setNodes(data.nodes ?? []);
        setEdges(data.edges ?? []);
      })
      .catch((err: unknown) => {
        setSituationError(err instanceof Error ? err.message : "Failed to load graph");
      })
      .finally(() => setSituationLoading(false));
  }, [workspaceId]);

  // Load reasoning traces when tab is first activated
  useEffect(() => {
    if (activeTab !== "reasoning" || traces.length > 0 || reasoningLoading) return;
    setReasoningLoading(true);
    setReasoningError(null);
    api.getReasoningTraces(workspaceId)
      .then((data) => setTraces(data.traces ?? []))
      .catch((err: unknown) => {
        setReasoningError(err instanceof Error ? err.message : "Failed to load reasoning traces");
      })
      .finally(() => setReasoningLoading(false));
  }, [activeTab, workspaceId, traces.length, reasoningLoading]);

  // Load theory assessments when tab is first activated
  useEffect(() => {
    if (activeTab !== "theories" || assessments.length > 0 || theoriesLoading) return;
    setTheoriesLoading(true);
    setTheoriesError(null);
    api.getTheoryAssessments(workspaceId)
      .then((data) => setAssessments(data.assessments ?? []))
      .catch((err: unknown) => {
        setTheoriesError(
          err instanceof Error ? err.message : "Failed to load theory assessments",
        );
      })
      .finally(() => setTheoriesLoading(false));
  }, [activeTab, workspaceId, assessments.length, theoriesLoading]);

  /* ── Graph editor callbacks ── */

  const handleAddNode = useCallback(
    async (node: { type: string; label: string }) => {
      const created = await api.addEntity(workspaceId, node);
      setNodes((prev) => [...prev, created]);
    },
    [workspaceId],
  );

  const handleDeleteNode = useCallback(
    async (nodeId: string) => {
      await api.deleteEntity(workspaceId, nodeId);
      setNodes((prev) => prev.filter((n) => n.id !== nodeId));
      setEdges((prev) =>
        prev.filter((e) => e.source !== nodeId && e.target !== nodeId),
      );
    },
    [workspaceId],
  );

  const handleAddEdge = useCallback(
    async (edge: { source: string; target: string; type: string }) => {
      const created = await api.addRelationship(workspaceId, edge);
      setEdges((prev) => [...prev, created]);
    },
    [workspaceId],
  );

  /* ── Reasoning validation callback ── */

  const handleValidateTrace = useCallback(
    async (
      traceId: string,
      verdict: "confirmed" | "rejected",
      notes?: string,
    ) => {
      const updated = await api.validateTrace(workspaceId, traceId, verdict, notes);
      setTraces((prev) =>
        prev.map((t) => (t.id === traceId ? { ...t, ...updated } : t)),
      );
    },
    [workspaceId],
  );

  /* ── Render ── */

  if (situationLoading) {
    return <PageSkeleton />;
  }

  return (
    <div className="space-y-5">
      {/* Back link */}
      <div>
        <Link
          href="/workspaces"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeft size={12} />
          All workspaces
        </Link>
      </div>

      {/* Workspace title */}
      <div>
        <h1 className="text-xl font-bold text-text-primary font-mono">
          ConflictCorpus
          <span className="ml-2 text-sm font-normal text-zinc-500">{workspaceId}</span>
        </h1>
        <p className="text-xs text-zinc-500 mt-0.5">
          {nodes.length} nodes &middot; {edges.length} edges
        </p>
      </div>

      {/* Tab bar */}
      <nav className="flex gap-1 border-b border-zinc-800 pb-px">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-1.5 px-4 py-2 text-sm border-b-2 transition-colors",
                activeTab === tab.id
                  ? "border-accent text-accent"
                  : "border-transparent text-zinc-500 hover:text-zinc-300",
              )}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* ── Situation tab ── */}
      {activeTab === "situation" && (
        <div className="space-y-3">
          {situationError && <ErrorBanner message={situationError} />}
          <div className="h-[600px]">
            <GraphEditor
              nodes={nodes}
              edges={edges}
              onAddNode={handleAddNode}
              onDeleteNode={handleDeleteNode}
              onAddEdge={handleAddEdge}
            />
          </div>
          <p className="text-[11px] text-zinc-600">
            {nodes.length} nodes &middot; {edges.length} edges &middot; Click canvas to add a
            node, shift-click nodes to draw edges, right-click for options.
          </p>
        </div>
      )}

      {/* ── Reasoning tab ── */}
      {activeTab === "reasoning" && (
        <div>
          {reasoningLoading && (
            <div className="space-y-2">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-14 w-full" />
              ))}
            </div>
          )}
          {reasoningError && <ErrorBanner message={reasoningError} />}
          {!reasoningLoading && !reasoningError && (
            <ReasoningPanel
              traces={traces}
              workspaceId={workspaceId}
              onValidate={handleValidateTrace}
            />
          )}
        </div>
      )}

      {/* ── Theories tab ── */}
      {activeTab === "theories" && (
        <div>
          {theoriesLoading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {[...Array(9)].map((_, i) => (
                <Skeleton key={i} className="h-44 w-full" />
              ))}
            </div>
          )}
          {theoriesError && <ErrorBanner message={theoriesError} />}
          {!theoriesLoading && !theoriesError && (
            <TheoryGrid assessments={assessments} />
          )}
        </div>
      )}
    </div>
  );
}
