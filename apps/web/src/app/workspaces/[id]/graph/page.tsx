'use client';

import { useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { AlertCircle, Loader2, Network } from 'lucide-react';
import { useGraphData } from '@/hooks/useGraph';
import type { GraphNode, GraphEdge } from '@/lib/api';
import { ForceGraph } from '@/components/graph/ForceGraph';
import { GraphControls } from '@/components/graph/GraphControls';
import { GraphLegend } from '@/components/graph/GraphLegend';
import { NodeDetail } from '@/components/graph/NodeDetail';
import { EdgeDetail } from '@/components/graph/EdgeDetail';

export default function GraphPage() {
  const params = useParams();
  const id = params.id as string;

  const { nodes, edges, loading, error, refetch } = useGraphData(id);

  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [layout, setLayout] = useState('force-directed');
  const [zoom, setZoom] = useState(1);
  const [visibleLabels, setVisibleLabels] = useState<string[]>([]);
  const [fitViewTrigger, setFitViewTrigger] = useState(0);
  const [resetTrigger, setResetTrigger] = useState(0);

  const handleNodeSelect = useCallback((node: GraphNode | null) => {
    setSelectedNode(node);
    if (node) setSelectedEdge(null);
  }, []);

  const handleEdgeSelect = useCallback((edge: GraphEdge | null) => {
    setSelectedEdge(edge);
    if (edge) setSelectedNode(null);
  }, []);

  const handleToggleLabel = useCallback((label: string) => {
    setVisibleLabels((prev) => {
      if (prev.includes(label)) return prev.filter((l) => l !== label);
      return [...prev, label];
    });
  }, []);

  const handleZoomIn  = useCallback(() => setZoom((z) => Math.min(z + 0.2, 4)), []);
  const handleZoomOut = useCallback(() => setZoom((z) => Math.max(z - 0.2, 0.2)), []);
  const handleFitView = useCallback(() => setFitViewTrigger((t) => t + 1), []);
  const handleReset   = useCallback(() => {
    setZoom(1);
    setResetTrigger((t) => t + 1);
  }, []);

  const hasDetail = selectedNode !== null || selectedEdge !== null;

  return (
    <div className="flex h-[calc(100vh-9.5rem)] overflow-hidden bg-[#09090b]">
      {/* Left panel */}
      <div className="flex flex-col gap-3 p-3 w-14 shrink-0 z-10">
        <GraphControls
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onReset={handleReset}
          onFitView={handleFitView}
          selectedLayout={layout}
          onLayoutChange={setLayout}
        />
      </div>

      {/* Canvas area */}
      <div className="relative flex-1 min-w-0 border-l border-r border-[#27272a]">
        {loading && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-[#09090b]/80 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 text-violet-500 animate-spin" />
              <p className="text-sm text-zinc-400">Loading graph…</p>
            </div>
          </div>
        )}

        {!loading && error && (
          <div className="absolute inset-0 z-20 flex items-center justify-center">
            <div className="rounded-xl border border-red-500/30 bg-[#18181b] p-6 flex items-start gap-3 max-w-sm">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-zinc-100">Failed to load graph</p>
                <p className="text-xs text-zinc-400 mt-1">{error}</p>
                <button
                  onClick={refetch}
                  className="mt-3 text-xs text-violet-400 hover:text-violet-300 underline"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && nodes.length === 0 && (
          <div className="absolute inset-0 z-10 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3 text-center">
              <Network className="w-12 h-12 text-zinc-700" />
              <p className="text-sm text-zinc-500">No nodes in this workspace yet.</p>
              <p className="text-xs text-zinc-600">Ingest documents to populate the graph.</p>
            </div>
          </div>
        )}

        <ForceGraph
          nodes={nodes}
          edges={edges}
          layout={layout}
          zoom={zoom}
          visibleLabels={visibleLabels.length > 0 ? visibleLabels : undefined}
          fitViewTrigger={fitViewTrigger}
          resetTrigger={resetTrigger}
          onNodeSelect={handleNodeSelect}
          onEdgeSelect={handleEdgeSelect}
          selectedNodeId={selectedNode?.id ?? null}
          selectedEdgeId={selectedEdge?.id ?? null}
        />

        {/* Stats overlay */}
        {!loading && !error && nodes.length > 0 && (
          <div className="absolute bottom-4 left-4 flex items-center gap-3 rounded-lg border border-[#27272a] bg-[#18181b]/90 backdrop-blur-sm px-3 py-1.5">
            <span className="text-xs text-zinc-400">
              <span className="font-semibold text-zinc-200">{nodes.length}</span> nodes
            </span>
            <span className="text-zinc-700">·</span>
            <span className="text-xs text-zinc-400">
              <span className="font-semibold text-zinc-200">{edges.length}</span> edges
            </span>
          </div>
        )}
      </div>

      {/* Right panel */}
      <div className="flex flex-col gap-3 p-3 w-56 shrink-0 overflow-y-auto">
        <GraphLegend
          visibleLabels={visibleLabels.length > 0 ? visibleLabels : undefined}
          onToggle={handleToggleLabel}
        />

        {hasDetail && (
          <div className="flex-1 min-h-0">
            {selectedNode && (
              <NodeDetail node={selectedNode} onClose={() => setSelectedNode(null)} />
            )}
            {selectedEdge && (
              <EdgeDetail edge={selectedEdge} onClose={() => setSelectedEdge(null)} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
