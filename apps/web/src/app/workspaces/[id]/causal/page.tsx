'use client';

import { useState, useMemo } from 'react';
import { useParams } from 'next/navigation';
import {
  GitBranch,
  AlertTriangle,
  Loader2,
  AlertCircle,
  RefreshCw,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';
import { useGraphData } from '@/hooks/useGraph';
import type { GraphNode, GraphEdge } from '@/lib/api';
import { CausalChainViz } from '@/components/graph/CausalChainViz';

// ─── Causal analysis helpers ───────────────────────────────────────────────────

function getCausalEdges(edges: GraphEdge[]): GraphEdge[] {
  return edges.filter((e) => {
    const t = e.type.toLowerCase();
    return t.includes('cause') || t.includes('causal') || t.includes('leads_to') || t.includes('triggers');
  });
}

/** Find nodes with no incoming causal edges — root causes */
function getRootCauses(nodes: GraphNode[], causalEdges: GraphEdge[]): GraphNode[] {
  const targetIds = new Set(causalEdges.map((e) => e.target_id));
  const sourceIds = new Set(causalEdges.map((e) => e.source_id));
  // Root = has outgoing causal edges but no incoming ones
  return nodes.filter(
    (n) => sourceIds.has(n.id) && !targetIds.has(n.id),
  );
}

/** Detect cycles via DFS */
function detectCycles(nodes: GraphNode[], edges: GraphEdge[]): string[][] {
  const adj: Record<string, string[]> = {};
  nodes.forEach((n) => { adj[n.id] = []; });
  edges.forEach((e) => {
    if (adj[e.source_id]) adj[e.source_id].push(e.target_id);
  });

  const visited = new Set<string>();
  const inStack = new Set<string>();
  const cycles: string[][] = [];

  function dfs(node: string, path: string[]) {
    if (inStack.has(node)) {
      const cycleStart = path.indexOf(node);
      cycles.push(path.slice(cycleStart));
      return;
    }
    if (visited.has(node)) return;
    visited.add(node);
    inStack.add(node);
    path.push(node);
    for (const next of (adj[node] ?? [])) {
      dfs(next, [...path]);
    }
    inStack.delete(node);
  }

  nodes.forEach((n) => {
    if (!visited.has(n.id)) dfs(n.id, []);
  });

  return cycles.slice(0, 5); // cap at 5 cycles for display
}

/** BFS chain depth from a root */
function getChainDepth(rootId: string, edges: GraphEdge[]): number {
  const adj: Record<string, string[]> = {};
  edges.forEach((e) => {
    if (!adj[e.source_id]) adj[e.source_id] = [];
    adj[e.source_id].push(e.target_id);
  });
  let depth = 0;
  const queue: [string, number][] = [[rootId, 0]];
  const visited = new Set<string>();
  while (queue.length > 0) {
    const [node, d] = queue.shift()!;
    if (visited.has(node)) continue;
    visited.add(node);
    depth = Math.max(depth, d);
    for (const next of (adj[node] ?? [])) {
      queue.push([next, d + 1]);
    }
  }
  return depth;
}

function nodeById(nodes: GraphNode[], id: string): GraphNode | undefined {
  return nodes.find((n) => n.id === id);
}

// ─── Page ──────────────────────────────────────────────────────────────────────

export default function CausalPage() {
  const params = useParams();
  const id = params.id as string;

  const { nodes, edges, loading, error, refetch } = useGraphData(id);

  const [showAllRoots, setShowAllRoots] = useState(false);

  const causalEdges = useMemo(() => getCausalEdges(edges), [edges]);
  const rootCauses  = useMemo(() => getRootCauses(nodes, causalEdges), [nodes, causalEdges]);
  const cycles      = useMemo(() => detectCycles(nodes, causalEdges), [nodes, causalEdges]);

  const rootsWithDepth = useMemo(
    () =>
      rootCauses.map((rc) => ({
        node: rc,
        depth: getChainDepth(rc.id, causalEdges),
      })).sort((a, b) => b.depth - a.depth),
    [rootCauses, causalEdges],
  );

  const displayedRoots = showAllRoots ? rootsWithDepth : rootsWithDepth.slice(0, 8);

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <GitBranch className="w-5 h-5 text-zinc-400" />
          <div>
            <h2 className="text-lg font-semibold text-zinc-100">Causal Analysis</h2>
            <p className="text-sm text-zinc-500">
              {loading
                ? 'Loading…'
                : `${causalEdges.length} causal link${causalEdges.length !== 1 ? 's' : ''} · ${rootCauses.length} root cause${rootCauses.length !== 1 ? 's' : ''}`}
            </p>
          </div>
        </div>
        <button
          onClick={refetch}
          disabled={loading}
          className="p-2 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-[#27272a] transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-7 h-7 text-violet-500 animate-spin" />
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <p className="text-sm text-zinc-400">{error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Cycle detection warnings */}
          {cycles.length > 0 && (
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-5 space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                <p className="text-sm font-semibold text-amber-400">
                  {cycles.length} Causal Cycle{cycles.length !== 1 ? 's' : ''} Detected
                </p>
              </div>
              <p className="text-xs text-zinc-500">
                Cycles indicate feedback loops in the causal graph, which may represent
                reinforcing dynamics or data inconsistencies.
              </p>
              <div className="space-y-2">
                {cycles.map((cycle, i) => (
                  <div
                    key={i}
                    className="flex flex-wrap items-center gap-1 rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2"
                  >
                    <RotateCcw className="w-3 h-3 text-amber-500 shrink-0" />
                    {cycle.map((nodeId, j) => {
                      const n = nodeById(nodes, nodeId);
                      return (
                        <span key={j} className="flex items-center gap-1">
                          <span className="text-xs text-zinc-300 font-medium">
                            {n?.name ?? nodeId.slice(0, 12)}
                          </span>
                          {j < cycle.length - 1 && (
                            <ArrowRight className="w-3 h-3 text-zinc-600" />
                          )}
                        </span>
                      );
                    })}
                    <ArrowRight className="w-3 h-3 text-amber-500" />
                    <span className="text-xs text-amber-400 font-medium">↺</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Causal chain visualiser */}
          <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
            <div className="px-5 py-3 border-b border-[#27272a]">
              <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
                Causal Chain Visualisation
              </p>
            </div>
            <CausalChainViz
              nodes={nodes}
              edges={causalEdges}
              workspaceId={id}
            />
          </div>

          {/* Root causes list */}
          {rootsWithDepth.length > 0 ? (
            <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
                  Root Causes ({rootCauses.length})
                </p>
                <p className="text-[10px] text-zinc-600">
                  Sorted by chain depth
                </p>
              </div>

              <div className="space-y-2">
                {displayedRoots.map(({ node, depth }) => (
                  <div
                    key={node.id}
                    className="flex items-center gap-3 rounded-lg border border-[#27272a] bg-zinc-900/30 px-3 py-2.5"
                  >
                    {/* Depth indicator */}
                    <div className="shrink-0 w-8 text-center">
                      <div className="rounded-md bg-violet-500/20 border border-violet-500/30 px-1 py-0.5">
                        <p className="text-[10px] font-bold text-violet-400">{depth}</p>
                      </div>
                      <p className="text-[9px] text-zinc-700 mt-0.5">depth</p>
                    </div>

                    {/* Node info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-zinc-200 truncate">
                        {node.name || node.id}
                      </p>
                      <p className="text-[10px] text-zinc-600 font-mono truncate">{node.id}</p>
                    </div>

                    {/* Label badge */}
                    <span className="shrink-0 rounded border border-[#27272a] bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-400 capitalize">
                      {node.label}
                    </span>
                  </div>
                ))}
              </div>

              {rootsWithDepth.length > 8 && (
                <button
                  onClick={() => setShowAllRoots((v) => !v)}
                  className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
                >
                  {showAllRoots
                    ? 'Show fewer'
                    : `Show all ${rootsWithDepth.length} root causes`}
                </button>
              )}
            </div>
          ) : (
            !loading && causalEdges.length === 0 && (
              <div className="rounded-xl border border-dashed border-[#27272a] p-12 text-center">
                <GitBranch className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
                <p className="text-sm text-zinc-600">
                  No causal relationships found in this workspace.
                </p>
                <p className="text-xs text-zinc-700 mt-1">
                  Ingest documents containing causal or "leads to" language to build causal chains.
                </p>
              </div>
            )
          )}

          {/* Chain depth stats */}
          {causalEdges.length > 0 && (
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Causal Links', value: causalEdges.length },
                { label: 'Root Causes', value: rootCauses.length },
                { label: 'Max Depth',   value: rootsWithDepth[0]?.depth ?? 0 },
              ].map(({ label, value }) => (
                <div
                  key={label}
                  className="rounded-xl border border-[#27272a] bg-[#18181b] px-4 py-3 text-center"
                >
                  <p className="text-2xl font-bold text-zinc-100">{value}</p>
                  <p className="text-xs text-zinc-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
