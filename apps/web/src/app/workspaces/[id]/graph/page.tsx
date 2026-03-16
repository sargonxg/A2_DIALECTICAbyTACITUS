"use client";

import { useState, useRef, useEffect } from "react";
import { useParams } from "next/navigation";
import { useGraphData } from "@/hooks/useGraph";
import ForceGraph from "@/components/graph/ForceGraph";
import GraphControls from "@/components/graph/GraphControls";
import GraphLegend from "@/components/graph/GraphLegend";
import NodeDetail from "@/components/graph/NodeDetail";
import EdgeDetail from "@/components/graph/EdgeDetail";
import type { GraphNode, GraphLink, LayoutType } from "@/types/graph";
import type { NodeType } from "@/types/ontology";

const ALL_NODE_TYPES = new Set<NodeType>([
  "actor", "conflict", "event", "issue", "interest", "norm", "process",
  "outcome", "narrative", "emotional_state", "trust_state", "power_dynamic",
  "location", "evidence", "role",
]);

export default function GraphPage() {
  const { id } = useParams();
  const { data, isLoading } = useGraphData(id as string);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<GraphLink | null>(null);
  const [activeNodeTypes, setActiveNodeTypes] = useState(new Set(ALL_NODE_TYPES));
  const [layout, setLayout] = useState<LayoutType>("force");
  const [confidence, setConfidence] = useState(0);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDims({ width, height });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const toggleNodeType = (type: NodeType) => {
    const next = new Set(activeNodeTypes);
    next.has(type) ? next.delete(type) : next.add(type);
    setActiveNodeTypes(next);
  };

  const filteredData = data ? {
    nodes: data.nodes.filter((n) => activeNodeTypes.has(n.node_type) && n.confidence >= confidence && (!search || n.name.toLowerCase().includes(search.toLowerCase()))),
    links: data.links.filter((l) => {
      const sId = typeof l.source === "string" ? l.source : l.source.id;
      const tId = typeof l.target === "string" ? l.target : l.target.id;
      const nodeIds = new Set(data.nodes.filter((n) => activeNodeTypes.has(n.node_type) && n.confidence >= confidence).map((n) => n.id));
      return nodeIds.has(sId) && nodeIds.has(tId);
    }),
  } : { nodes: [], links: [] };

  if (isLoading) return <div className="card h-96 animate-pulse bg-surface-hover" />;

  return (
    <div className="flex gap-4 h-[calc(100vh-14rem)]">
      <div className="w-64 flex-shrink-0 space-y-4 overflow-y-auto">
        <GraphControls
          activeNodeTypes={activeNodeTypes}
          onToggleNodeType={toggleNodeType}
          layout={layout}
          onLayoutChange={setLayout}
          confidenceThreshold={confidence}
          onConfidenceChange={setConfidence}
          searchQuery={search}
          onSearchChange={setSearch}
          onFitToScreen={() => {}}
          onExport={() => {}}
        />
        <GraphLegend />
      </div>

      <div ref={containerRef} className="flex-1 relative bg-background rounded-lg border border-border overflow-hidden">
        <ForceGraph
          data={filteredData}
          width={dims.width}
          height={dims.height}
          onNodeClick={(n) => { setSelectedNode(n); setSelectedLink(null); }}
          onEdgeClick={(l) => { setSelectedLink(l); setSelectedNode(null); }}
          selectedNodeId={selectedNode?.id}
        />

        {/* Detail sidebars */}
        {selectedNode && (
          <div className="absolute top-4 right-4 z-10">
            <NodeDetail node={selectedNode} onClose={() => setSelectedNode(null)} />
          </div>
        )}
        {selectedLink && (
          <div className="absolute top-4 right-4 z-10">
            <EdgeDetail link={selectedLink} onClose={() => setSelectedLink(null)} />
          </div>
        )}
      </div>
    </div>
  );
}
