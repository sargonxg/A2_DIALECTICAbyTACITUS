"use client";

import {
  useRef,
  useEffect,
  useState,
  useCallback,
  type MouseEvent,
} from "react";
import * as d3 from "d3";
import { X, Plus } from "lucide-react";
import { cn, NODE_COLORS } from "@/lib/utils";
import type { GraphNode, GraphEdge } from "@/types/api";

const NODE_TYPES = [
  "Actor",
  "Event",
  "Issue",
  "Interest",
  "Norm",
  "Process",
  "Outcome",
  "Narrative",
  "EmotionalState",
  "TrustState",
  "PowerDynamic",
  "Location",
  "Evidence",
  "Role",
] as const;

const EDGE_TYPES = [
  "CAUSED",
  "PARTICIPATED_IN",
  "HAS_INTEREST",
  "OPPOSES",
  "SUPPORTS",
  "VIOLATES",
  "GOVERNS",
  "LED_TO",
  "ESCALATED_BY",
  "DE_ESCALATED_BY",
  "LOCATED_IN",
  "INVOLVES",
  "ASSESSED_VIA",
  "TRUSTS",
  "HOLDS_POWER_OVER",
] as const;

export interface GraphEditorProps {
  nodes: Array<GraphNode>;
  edges: Array<GraphEdge>;
  onAddNode: (node: { type: string; label: string }) => Promise<void>;
  onDeleteNode: (nodeId: string) => Promise<void>;
  onAddEdge: (edge: { source: string; target: string; type: string }) => Promise<void>;
  readOnly?: boolean;
}

interface ContextMenu {
  x: number;
  y: number;
  nodeId: string;
}

interface AddNodeModal {
  x: number;
  y: number;
}

interface AddEdgeModal {
  sourceId: string;
}

type SimNode = GraphNode & d3.SimulationNodeDatum;
interface SimLink {
  source: SimNode;
  target: SimNode;
  type: string;
  id?: string;
}

function nodeColor(type: string): string {
  const key = type.toLowerCase().replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase();
  return NODE_COLORS[key] ?? "#6366f1";
}

export default function GraphEditor({
  nodes,
  edges,
  onAddNode,
  onDeleteNode,
  onAddEdge,
  readOnly = false,
}: GraphEditorProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [contextMenu, setContextMenu] = useState<ContextMenu | null>(null);
  const [addNodeModal, setAddNodeModal] = useState<AddNodeModal | null>(null);
  const [addEdgeModal, setAddEdgeModal] = useState<AddEdgeModal | null>(null);
  const [pendingEdgeSource, setPendingEdgeSource] = useState<string | null>(null);

  // Modal form state
  const [newNodeType, setNewNodeType] = useState<string>(NODE_TYPES[0]);
  const [newNodeLabel, setNewNodeLabel] = useState("");
  const [newEdgeType, setNewEdgeType] = useState<string>(EDGE_TYPES[0]);
  const [saving, setSaving] = useState(false);

  const closeAll = useCallback(() => {
    setContextMenu(null);
    setAddNodeModal(null);
    setAddEdgeModal(null);
    setPendingEdgeSource(null);
    setNewNodeLabel("");
    setNewNodeType(NODE_TYPES[0]);
    setNewEdgeType(EDGE_TYPES[0]);
  }, []);

  // Build D3 simulation
  useEffect(() => {
    const svg = svgRef.current;
    const container = containerRef.current;
    if (!svg || !container) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    const svgSel = d3.select(svg);
    svgSel.selectAll("*").remove();
    svgSel.attr("viewBox", `0 0 ${width} ${height}`);

    // Zoom layer
    const g = svgSel.append("g");
    svgSel.call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => g.attr("transform", event.transform)),
    );

    // Click on background → add node
    svgSel.on("click", (event: MouseEvent) => {
      if (readOnly) return;
      const target = event.target as SVGElement;
      if (target === svg || target.tagName === "rect") {
        const [x, y] = d3.pointer(event, svg);
        setAddNodeModal({ x, y });
      }
    });

    // Background rect for click capture
    g.append("rect")
      .attr("width", width)
      .attr("height", height)
      .attr("fill", "transparent");

    // Arrow defs
    const defs = svgSel.append("defs");
    defs.append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 20)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#64748b");

    const simNodes: SimNode[] = nodes.map((n) => ({ ...n }));
    const nodeById = new Map(simNodes.map((n) => [n.id, n]));

    const simLinksRaw = edges.map((e) => {
      const source = nodeById.get(typeof e.source === "string" ? e.source : "");
      const target = nodeById.get(typeof e.target === "string" ? e.target : "");
      if (!source || !target) return null;
      return { source, target, type: e.type, id: e.id } as SimLink;
    });
    const simLinks: SimLink[] = simLinksRaw.filter(
      (l): l is NonNullable<typeof l> => l !== null,
    );

    const simulation = d3
      .forceSimulation<SimNode>(simNodes)
      .force("link", d3.forceLink<SimNode, SimLink>(simLinks).id((d) => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide(24));

    // Links
    const link = g
      .append("g")
      .attr("stroke", "#334155")
      .selectAll("line")
      .data(simLinks)
      .join("line")
      .attr("stroke-width", 1.5)
      .attr("marker-end", "url(#arrow)");

    // Link labels
    const linkLabel = g
      .append("g")
      .selectAll("text")
      .data(simLinks)
      .join("text")
      .attr("font-size", 9)
      .attr("fill", "#64748b")
      .attr("text-anchor", "middle")
      .text((d) => d.type);

    // Node groups
    const nodeGroup = g
      .append("g")
      .selectAll<SVGGElement, SimNode>("g")
      .data(simNodes)
      .join("g")
      .attr("cursor", "pointer")
      .call(
        d3.drag<SVGGElement, SimNode>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }),
      );

    nodeGroup
      .append("circle")
      .attr("r", 14)
      .attr("fill", (d) => nodeColor(d.type))
      .attr("fill-opacity", 0.85)
      .attr("stroke", "#0f172a")
      .attr("stroke-width", 1.5);

    nodeGroup
      .append("text")
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .attr("font-size", 8)
      .attr("fill", "#fff")
      .attr("pointer-events", "none")
      .text((d) => d.type.slice(0, 2).toUpperCase());

    nodeGroup
      .append("text")
      .attr("dy", 26)
      .attr("text-anchor", "middle")
      .attr("font-size", 10)
      .attr("fill", "#cbd5e1")
      .attr("pointer-events", "none")
      .text((d) => (d.label.length > 14 ? d.label.slice(0, 12) + "…" : d.label));

    // Click on node
    nodeGroup.on("click", (event: MouseEvent, d: SimNode) => {
      event.stopPropagation();
      if (!readOnly && pendingEdgeSource && pendingEdgeSource !== d.id) {
        // Shift-click (or second click while pending) → open add edge modal
        setAddEdgeModal({ sourceId: pendingEdgeSource });
        setAddEdgeModal({ sourceId: pendingEdgeSource });
        // Store target in a closure-safe way via a hidden dataset
        (svg as unknown as { __edgeTarget?: string }).__edgeTarget = d.id;
        setAddEdgeModal({ sourceId: pendingEdgeSource });
        return;
      }
      setSelectedNode(d);
      setContextMenu(null);
    });

    // Shift-click on node to start edge
    nodeGroup.on("click.edge", (event: MouseEvent, d: SimNode) => {
      if (readOnly || !event.shiftKey) return;
      event.stopPropagation();
      if (!pendingEdgeSource) {
        setPendingEdgeSource(d.id);
      } else if (pendingEdgeSource !== d.id) {
        (svg as unknown as { __edgeTarget?: string }).__edgeTarget = d.id;
        setAddEdgeModal({ sourceId: pendingEdgeSource });
      }
    });

    // Right-click context menu
    nodeGroup.on("contextmenu", (event: MouseEvent, d: SimNode) => {
      if (readOnly) return;
      event.preventDefault();
      event.stopPropagation();
      setContextMenu({ x: event.clientX, y: event.clientY, nodeId: d.id });
    });

    // Tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as SimNode).x ?? 0)
        .attr("y1", (d) => (d.source as SimNode).y ?? 0)
        .attr("x2", (d) => (d.target as SimNode).x ?? 0)
        .attr("y2", (d) => (d.target as SimNode).y ?? 0);

      linkLabel
        .attr("x", (d) => (((d.source as SimNode).x ?? 0) + ((d.target as SimNode).x ?? 0)) / 2)
        .attr("y", (d) => (((d.source as SimNode).y ?? 0) + ((d.target as SimNode).y ?? 0)) / 2);

      nodeGroup.attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, readOnly, pendingEdgeSource]);

  // Handlers
  const handleAddNode = useCallback(async () => {
    if (!newNodeLabel.trim()) return;
    setSaving(true);
    try {
      await onAddNode({ type: newNodeType, label: newNodeLabel.trim() });
      closeAll();
    } finally {
      setSaving(false);
    }
  }, [newNodeLabel, newNodeType, onAddNode, closeAll]);

  const handleDeleteNode = useCallback(async (nodeId: string) => {
    setSaving(true);
    try {
      await onDeleteNode(nodeId);
      setSelectedNode(null);
      closeAll();
    } finally {
      setSaving(false);
    }
  }, [onDeleteNode, closeAll]);

  const handleAddEdge = useCallback(async () => {
    if (!addEdgeModal) return;
    const svg = svgRef.current as unknown as { __edgeTarget?: string } | null;
    const targetId = svg?.__edgeTarget;
    if (!targetId) return;
    setSaving(true);
    try {
      await onAddEdge({ source: addEdgeModal.sourceId, target: targetId, type: newEdgeType });
      closeAll();
    } finally {
      setSaving(false);
    }
  }, [addEdgeModal, newEdgeType, onAddEdge, closeAll]);

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[500px] bg-zinc-950 rounded-lg overflow-hidden border border-zinc-800"
      onClick={() => setContextMenu(null)}
    >
      <svg ref={svgRef} className="w-full h-full" />

      {/* Pending edge hint */}
      {pendingEdgeSource && !readOnly && (
        <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-blue-900/80 text-blue-200 text-xs px-3 py-1.5 rounded-full pointer-events-none">
          Shift-click a target node to draw an edge — or{" "}
          <button
            className="underline pointer-events-auto"
            onClick={(e) => { e.stopPropagation(); closeAll(); }}
          >
            cancel
          </button>
        </div>
      )}

      {!readOnly && (
        <div className="absolute bottom-3 right-3 text-[10px] text-zinc-600">
          Click canvas → add node &nbsp;|&nbsp; Shift-click node → draw edge &nbsp;|&nbsp; Right-click node → options
        </div>
      )}

      {/* Node properties panel */}
      {selectedNode && (
        <aside className="absolute top-2 right-2 w-56 bg-zinc-900/95 border border-zinc-700 rounded-lg p-3 text-xs space-y-2 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-white truncate">{selectedNode.label}</span>
            <button onClick={() => setSelectedNode(null)} className="text-zinc-500 hover:text-white">
              <X size={14} />
            </button>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: nodeColor(selectedNode.type) }}
            />
            <span className="text-zinc-400">{selectedNode.type}</span>
          </div>
          <div className="text-zinc-500 font-mono text-[10px] break-all">{selectedNode.id}</div>
          {Object.entries(selectedNode.properties).length > 0 && (
            <div className="space-y-1 border-t border-zinc-800 pt-2">
              {Object.entries(selectedNode.properties).slice(0, 6).map(([k, v]) => (
                <div key={k} className="flex gap-1 text-[10px]">
                  <span className="text-zinc-500 shrink-0">{k}:</span>
                  <span className="text-zinc-300 truncate">{String(v)}</span>
                </div>
              ))}
            </div>
          )}
          {!readOnly && (
            <button
              onClick={() => handleDeleteNode(selectedNode.id)}
              disabled={saving}
              className="w-full text-red-400 hover:text-red-300 border border-red-900/50 rounded px-2 py-1 text-[10px] transition-colors disabled:opacity-50"
            >
              Delete node
            </button>
          )}
        </aside>
      )}

      {/* Context menu */}
      {contextMenu && !readOnly && (
        <div
          className="fixed z-50 bg-zinc-900 border border-zinc-700 rounded-md shadow-xl py-1 text-xs min-w-[120px]"
          style={{ top: contextMenu.y, left: contextMenu.x }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            className="w-full px-3 py-1.5 text-left text-zinc-300 hover:bg-zinc-800"
            onClick={() => {
              const node = nodes.find((n) => n.id === contextMenu.nodeId);
              if (node) setSelectedNode(node);
              setContextMenu(null);
            }}
          >
            View details
          </button>
          <button
            className="w-full px-3 py-1.5 text-left text-zinc-300 hover:bg-zinc-800"
            onClick={() => {
              setPendingEdgeSource(contextMenu.nodeId);
              setContextMenu(null);
            }}
          >
            Draw edge from here
          </button>
          <button
            className="w-full px-3 py-1.5 text-left text-red-400 hover:bg-zinc-800"
            onClick={() => {
              handleDeleteNode(contextMenu.nodeId);
            }}
          >
            Delete
          </button>
        </div>
      )}

      {/* Add Node Modal */}
      {addNodeModal && !readOnly && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 z-40">
          <div
            className="bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl p-5 w-72 space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Plus size={16} className="text-blue-400" />
                Add Node
              </h3>
              <button onClick={closeAll} className="text-zinc-500 hover:text-white">
                <X size={16} />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Node type</label>
                <select
                  value={newNodeType}
                  onChange={(e) => setNewNodeType(e.target.value)}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  {NODE_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Label</label>
                <input
                  type="text"
                  value={newNodeLabel}
                  onChange={(e) => setNewNodeLabel(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleAddNode()}
                  placeholder="Node name…"
                  className="w-full bg-zinc-800 border border-zinc-700 rounded px-2 py-1.5 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={closeAll}
                className="flex-1 px-3 py-1.5 rounded bg-zinc-800 text-zinc-300 text-sm hover:bg-zinc-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddNode}
                disabled={!newNodeLabel.trim() || saving}
                className="flex-1 px-3 py-1.5 rounded bg-blue-600 text-white text-sm hover:bg-blue-500 transition-colors disabled:opacity-50"
              >
                {saving ? "Adding…" : "Add"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Edge Modal */}
      {addEdgeModal && !readOnly && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 z-40">
          <div
            className="bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl p-5 w-72 space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Add Edge</h3>
              <button onClick={closeAll} className="text-zinc-500 hover:text-white">
                <X size={16} />
              </button>
            </div>

            <div className="text-[11px] text-zinc-400">
              From <span className={cn("text-blue-300 font-mono")}>{addEdgeModal.sourceId.slice(0, 12)}…</span>
            </div>

            <div>
              <label className="block text-[11px] text-zinc-400 mb-1">Edge type</label>
              <select
                value={newEdgeType}
                onChange={(e) => setNewEdgeType(e.target.value)}
                className="w-full bg-zinc-800 border border-zinc-700 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                {EDGE_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="flex gap-2">
              <button
                onClick={closeAll}
                className="flex-1 px-3 py-1.5 rounded bg-zinc-800 text-zinc-300 text-sm hover:bg-zinc-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddEdge}
                disabled={saving}
                className="flex-1 px-3 py-1.5 rounded bg-blue-600 text-white text-sm hover:bg-blue-500 transition-colors disabled:opacity-50"
              >
                {saving ? "Adding…" : "Add edge"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
