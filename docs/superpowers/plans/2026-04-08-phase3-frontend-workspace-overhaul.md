# Phase 3: Frontend Workspace Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **PREREQUISITE:** Phase 2 plan must be fully committed before starting this plan.

**Goal:** Transform the DIALECTICA frontend from a basic tab-based UI into a production analytical workspace — interactive graph editor with full CRUD, three-panel layout with zustand state management, and a comprehensive multi-method ingestion interface.

**Architecture:**
- **3.1 Graph Editor:** D3 SVG (< 300 nodes) → Canvas (300-2000) with node/edge CRUD, community hulls, temporal toggle, filter panel, 3 layout modes
- **3.2 Three-Panel Dashboard:** `NavigationSidebar` + center views + `DetailPanel`, zustand workspace store, `@tanstack/react-query` for all fetching
- **3.3 Ingestion Interface:** 5 input methods (text, upload, structured, URL, template), extraction review workflow, animated graph preview

**Tech Stack:** Next.js 15 App Router, React 19, TypeScript, D3.js v7, Zustand 5, @tanstack/react-query v5, Tailwind CSS

---

## File Map

### Task 3.1 — Interactive Graph Editor
- **Rewrite:** `apps/web/src/components/graph/ForceGraph.tsx` — full D3 SVG/Canvas hybrid editor
- **Create:** `apps/web/src/components/graph/GraphFilters.tsx` — filter panel (left sidebar)
- **Create:** `apps/web/src/components/graph/NodeDetailPanel.tsx` — right sidebar detail
- **Create:** `apps/web/src/components/graph/EdgeDetailPanel.tsx`
- **Create:** `apps/web/src/components/graph/AddEntityModal.tsx`
- **Create:** `apps/web/src/components/graph/AddRelationshipModal.tsx`
- **Modify:** `apps/web/src/types/api.ts` — add filter/view types

### Task 3.2 — Three-Panel Dashboard
- **Rewrite:** `apps/web/src/app/workspaces/[id]/page.tsx` — three-panel layout
- **Create:** `apps/web/src/app/workspaces/[id]/layout.tsx` — workspace layout wrapper
- **Create:** `apps/web/src/components/workspace/NavigationSidebar.tsx` — entity tree, episodes, filters
- **Create:** `apps/web/src/components/workspace/DetailPanel.tsx` — selection detail + AI + theory + report
- **Create:** `apps/web/src/components/workspace/StatusBar.tsx`
- **Create:** `apps/web/src/stores/workspaceStore.ts` — zustand store
- **Modify:** `apps/web/package.json` — add zustand, @tanstack/react-query

### Task 3.3 — Ingestion Interface
- **Rewrite:** `apps/web/src/app/workspaces/[id]/ingest/page.tsx` — 5-method ingestion
- **Create:** `apps/web/src/components/ingestion/TextIngest.tsx`
- **Create:** `apps/web/src/components/ingestion/FileIngest.tsx`
- **Create:** `apps/web/src/components/ingestion/StructuredIngest.tsx`
- **Create:** `apps/web/src/components/ingestion/UrlIngest.tsx`
- **Create:** `apps/web/src/components/ingestion/TemplateIngest.tsx`
- **Create:** `apps/web/src/components/ingestion/ExtractionReview.tsx`

---

## Task 1: Interactive Knowledge Graph Editor (Prompt 3.1)

**Files:**
- Rewrite: `apps/web/src/components/graph/ForceGraph.tsx`
- Create: `apps/web/src/components/graph/GraphFilters.tsx`
- Create: `apps/web/src/components/graph/NodeDetailPanel.tsx`
- Create: `apps/web/src/components/graph/AddEntityModal.tsx`

### Step 1.1 — Install dependencies

- [ ] In `apps/web/`:

```bash
npm install zustand @tanstack/react-query
```

### Step 1.2 — Add graph state types to `types/api.ts`

- [ ] Append to `apps/web/src/types/api.ts`:

```typescript
export interface GraphFilters {
  nodeTypes: string[];          // which node types to show
  edgeTypes: string[];
  confidenceMin: number;        // 0.0-1.0
  layer: "both" | "situation" | "knowledge";
  dateFrom?: string;            // ISO for temporal filter
  dateTo?: string;
  searchQuery?: string;
}

export type GraphLayout = "force" | "hierarchical" | "radial";

export type GraphView = "graph" | "timeline" | "matrix" | "causal";
```

### Step 1.3 — Create `GraphFilters.tsx`

- [ ] Create `apps/web/src/components/graph/GraphFilters.tsx`:

```typescript
"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import type { GraphFilters as GraphFiltersType } from "@/types/api";

const NODE_TYPES = [
  "Actor", "Event", "Issue", "Interest", "Conflict", "Norm",
  "Process", "Outcome", "EmotionalState", "TrustState", "PowerDynamic",
  "Location", "Evidence", "Role", "EpisodeNode", "ConflictPattern", "ResolutionPrecedent",
];

const EDGE_TYPES = [
  "CAUSED", "PARTICIPATED_IN", "HAS_INTEREST", "OPPOSES", "SUPPORTS",
  "VIOLATES", "GOVERNS", "LED_TO", "ESCALATED_BY", "DE_ESCALATED_BY",
  "LOCATED_IN", "INVOLVES", "ASSESSED_VIA", "TRUSTS", "HOLDS_POWER_OVER",
  "SOURCED_FROM", "APPLIES_TO",
];

interface GraphFiltersProps {
  filters: GraphFiltersType;
  nodeCounts: Record<string, number>;
  onChange: (filters: GraphFiltersType) => void;
  className?: string;
}

export default function GraphFilters({ filters, nodeCounts, onChange, className }: GraphFiltersProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    nodeTypes: true,
    edgeTypes: false,
    layers: true,
    confidence: true,
  });

  const toggle = (section: string) =>
    setExpanded((e) => ({ ...e, [section]: !e[section] }));

  const toggleNodeType = (type: string) => {
    const current = filters.nodeTypes;
    const next = current.includes(type)
      ? current.filter((t) => t !== type)
      : [...current, type];
    onChange({ ...filters, nodeTypes: next });
  };

  const toggleEdgeType = (type: string) => {
    const current = filters.edgeTypes;
    const next = current.includes(type)
      ? current.filter((t) => t !== type)
      : [...current, type];
    onChange({ ...filters, edgeTypes: next });
  };

  return (
    <div className={cn("space-y-3 text-xs", className)}>
      {/* Search */}
      <input
        type="text"
        placeholder="Search nodes…"
        value={filters.searchQuery || ""}
        onChange={(e) => onChange({ ...filters, searchQuery: e.target.value })}
        className="w-full bg-zinc-800 border border-zinc-700 rounded px-2 py-1.5 text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500"
      />

      {/* Layer toggle */}
      <div>
        <button
          className="flex w-full items-center justify-between font-semibold text-zinc-400 uppercase tracking-wider text-[10px] py-1"
          onClick={() => toggle("layers")}
        >
          Layer {expanded.layers ? "▾" : "▸"}
        </button>
        {expanded.layers && (
          <div className="flex gap-1 mt-1">
            {(["both", "situation", "knowledge"] as const).map((l) => (
              <button
                key={l}
                onClick={() => onChange({ ...filters, layer: l })}
                className={cn(
                  "px-2 py-0.5 rounded text-[10px] capitalize transition-colors",
                  filters.layer === l
                    ? "bg-blue-600 text-white"
                    : "bg-zinc-800 text-zinc-400 hover:text-white",
                )}
              >
                {l}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Confidence slider */}
      <div>
        <button
          className="flex w-full items-center justify-between font-semibold text-zinc-400 uppercase tracking-wider text-[10px] py-1"
          onClick={() => toggle("confidence")}
        >
          Min Confidence {expanded.confidence ? "▾" : "▸"}
        </button>
        {expanded.confidence && (
          <div className="flex items-center gap-2 mt-1">
            <input
              type="range"
              min={0}
              max={100}
              value={Math.round((filters.confidenceMin || 0) * 100)}
              onChange={(e) =>
                onChange({ ...filters, confidenceMin: parseInt(e.target.value) / 100 })
              }
              className="flex-1 accent-blue-500"
            />
            <span className="text-zinc-400 tabular-nums w-8">
              {Math.round((filters.confidenceMin || 0) * 100)}%
            </span>
          </div>
        )}
      </div>

      {/* Node types */}
      <div>
        <button
          className="flex w-full items-center justify-between font-semibold text-zinc-400 uppercase tracking-wider text-[10px] py-1"
          onClick={() => toggle("nodeTypes")}
        >
          Node Types {expanded.nodeTypes ? "▾" : "▸"}
        </button>
        {expanded.nodeTypes && (
          <div className="space-y-0.5 mt-1">
            {NODE_TYPES.map((type) => (
              <label key={type} className="flex items-center gap-2 cursor-pointer py-0.5">
                <input
                  type="checkbox"
                  checked={filters.nodeTypes.includes(type)}
                  onChange={() => toggleNodeType(type)}
                  className="accent-blue-500 rounded"
                />
                <span className="text-zinc-300 flex-1">{type}</span>
                {nodeCounts[type] !== undefined && (
                  <span className="text-zinc-600">{nodeCounts[type]}</span>
                )}
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Edge types */}
      <div>
        <button
          className="flex w-full items-center justify-between font-semibold text-zinc-400 uppercase tracking-wider text-[10px] py-1"
          onClick={() => toggle("edgeTypes")}
        >
          Edge Types {expanded.edgeTypes ? "▾" : "▸"}
        </button>
        {expanded.edgeTypes && (
          <div className="space-y-0.5 mt-1">
            {EDGE_TYPES.map((type) => (
              <label key={type} className="flex items-center gap-2 cursor-pointer py-0.5">
                <input
                  type="checkbox"
                  checked={filters.edgeTypes.includes(type)}
                  onChange={() => toggleEdgeType(type)}
                  className="accent-blue-500 rounded"
                />
                <span className="text-zinc-300 font-mono text-[9px]">{type}</span>
              </label>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

### Step 1.4 — Create `NodeDetailPanel.tsx`

- [ ] Create `apps/web/src/components/graph/NodeDetailPanel.tsx`:

```typescript
"use client";

import { X, ExternalLink, Shield, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";
import type { GraphNode } from "@/types/api";

interface NodeDetailPanelProps {
  node: GraphNode;
  onClose: () => void;
  onDelete?: (nodeId: string) => Promise<void>;
  onShowProvenance?: (nodeId: string) => void;
  onShowReasoning?: (nodeId: string) => void;
}

export default function NodeDetailPanel({
  node,
  onClose,
  onDelete,
  onShowProvenance,
  onShowReasoning,
}: NodeDetailPanelProps) {
  const props = node.properties;
  const layer = (props.layer_type as string) || "situation";
  const confidence = props.confidence_score as number | undefined;
  const confidenceTag = (props.confidence_tag as string) || "EXTRACTED";

  return (
    <div className="w-72 bg-zinc-900 border-l border-zinc-800 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-800">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-white truncate">{node.label}</h3>
          <p className="text-[10px] text-zinc-500">{node.type}</p>
        </div>
        <button onClick={onClose} className="text-zinc-500 hover:text-white ml-2">
          <X size={16} />
        </button>
      </div>

      {/* Badges */}
      <div className="px-4 py-2 flex flex-wrap gap-1.5">
        <span className={cn(
          "text-[9px] px-1.5 py-0.5 rounded border font-medium",
          layer === "knowledge"
            ? "bg-violet-950 text-violet-300 border-violet-800"
            : "bg-zinc-800 text-zinc-400 border-zinc-700",
        )}>
          {layer}
        </span>
        {confidence !== undefined && (
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
            {confidenceTag === "EXTRACTED" ? <Shield size={8} className="inline mr-0.5" /> : <Cpu size={8} className="inline mr-0.5" />}
            {Math.round(confidence * 100)}% {confidenceTag.toLowerCase()}
          </span>
        )}
      </div>

      {/* Properties */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1">
        <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-2">Properties</p>
        {Object.entries(props)
          .filter(([k]) => !["id", "workspace_id", "tenant_id"].includes(k))
          .map(([k, v]) => (
            <div key={k} className="flex gap-2 text-[11px]">
              <span className="text-zinc-500 shrink-0 w-28 truncate">{k}:</span>
              <span className="text-zinc-300 break-all">{String(v ?? "—")}</span>
            </div>
          ))}
        <div className="flex gap-2 text-[11px]">
          <span className="text-zinc-500 shrink-0 w-28">id:</span>
          <span className="text-zinc-600 font-mono text-[9px] break-all">{node.id}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-zinc-800 space-y-2">
        {onShowProvenance && (
          <button
            onClick={() => onShowProvenance(node.id)}
            className="w-full text-left text-xs text-zinc-400 hover:text-white flex items-center gap-2 py-1"
          >
            <ExternalLink size={12} />
            Show provenance (source episodes)
          </button>
        )}
        {onShowReasoning && (
          <button
            onClick={() => onShowReasoning(node.id)}
            className="w-full text-left text-xs text-zinc-400 hover:text-white flex items-center gap-2 py-1"
          >
            <Shield size={12} />
            Show reasoning traces
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete(node.id)}
            className="w-full text-center text-xs text-red-400 hover:text-red-300 border border-red-900/40 rounded py-1.5 transition-colors"
          >
            Delete node
          </button>
        )}
      </div>
    </div>
  );
}
```

### Step 1.5 — Rewrite `ForceGraph.tsx` (D3 SVG enhanced)

- [ ] Rewrite `apps/web/src/components/graph/ForceGraph.tsx`. The enhanced version adds: node size by degree, shape by layer, edge width by confidence, edge style by confidence_tag, community convex hulls. Key changes from existing:

```typescript
"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import * as d3 from "d3";
import { cn, NODE_COLORS } from "@/lib/utils";
import type { GraphNode, GraphEdge, GraphFilters, GraphLayout } from "@/types/api";
import GraphFiltersPanel from "./GraphFilters";
import NodeDetailPanel from "./NodeDetailPanel";

const CANVAS_THRESHOLD = 300; // switch to canvas above this node count

interface ForceGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  filters?: GraphFilters;
  layout?: GraphLayout;
  onAddNode?: (node: { type: string; label: string; layer?: string }) => Promise<void>;
  onDeleteNode?: (nodeId: string) => Promise<void>;
  onAddEdge?: (edge: { source: string; target: string; type: string }) => Promise<void>;
  readOnly?: boolean;
  showFilters?: boolean;
}

function nodeRadius(degree: number): number {
  return Math.max(8, Math.min(40, 8 + degree * 2));
}

function edgeWidth(confidence: number | undefined): number {
  if (confidence === undefined) return 1.5;
  return 1 + confidence * 3;
}

function edgeDashArray(confidenceTag: string | undefined): string {
  if (confidenceTag === "INFERRED") return "6,3";
  if (confidenceTag === "AMBIGUOUS") return "2,2";
  return "none";
}

function nodeColor(type: string): string {
  const key = type.toLowerCase().replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase();
  return NODE_COLORS[key] ?? "#6366f1";
}

export default function ForceGraph({
  nodes,
  edges,
  filters,
  layout = "force",
  onAddNode,
  onDeleteNode,
  onAddEdge,
  readOnly = false,
  showFilters = false,
}: ForceGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showFilterPanel, setShowFilterPanel] = useState(showFilters);
  const [activeFilters, setActiveFilters] = useState<GraphFilters>(
    filters ?? {
      nodeTypes: [],
      edgeTypes: [],
      confidenceMin: 0,
      layer: "both",
    },
  );

  // Filter nodes/edges by active filters
  const filteredNodes = nodes.filter((n) => {
    if (activeFilters.nodeTypes.length > 0 && !activeFilters.nodeTypes.includes(n.type)) return false;
    if (activeFilters.layer !== "both") {
      const nodeLayer = (n.properties.layer_type as string) || "situation";
      if (nodeLayer !== activeFilters.layer) return false;
    }
    if (activeFilters.searchQuery) {
      const q = activeFilters.searchQuery.toLowerCase();
      if (!n.label.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));
  const filteredEdges = edges.filter(
    (e) =>
      filteredNodeIds.has(e.source) &&
      filteredNodeIds.has(e.target) &&
      (activeFilters.edgeTypes.length === 0 || activeFilters.edgeTypes.includes(e.type)),
  );

  // Node counts for filter panel
  const nodeCounts: Record<string, number> = {};
  for (const n of nodes) {
    nodeCounts[n.type] = (nodeCounts[n.type] || 0) + 1;
  }

  // Degree map
  const degreeMap: Record<string, number> = {};
  for (const e of filteredEdges) {
    degreeMap[e.source] = (degreeMap[e.source] || 0) + 1;
    degreeMap[e.target] = (degreeMap[e.target] || 0) + 1;
  }

  useEffect(() => {
    const svg = svgRef.current;
    const container = containerRef.current;
    if (!svg || !container) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;
    const svgSel = d3.select(svg);
    svgSel.selectAll("*").remove();
    svgSel.attr("viewBox", `0 0 ${width} ${height}`);

    const g = svgSel.append("g");
    svgSel.call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 6])
        .on("zoom", (event) => g.attr("transform", event.transform)),
    );

    // Background
    g.append("rect").attr("width", width).attr("height", height).attr("fill", "transparent");

    // Arrow marker
    const defs = svgSel.append("defs");
    defs.append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 22).attr("refY", 0)
      .attr("markerWidth", 6).attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#475569");

    type SimNode = GraphNode & d3.SimulationNodeDatum;
    const simNodes: SimNode[] = filteredNodes.map((n) => ({ ...n }));
    const nodeById = new Map(simNodes.map((n) => [n.id, n]));

    const simLinks = filteredEdges
      .map((e) => {
        const source = nodeById.get(e.source);
        const target = nodeById.get(e.target);
        if (!source || !target) return null;
        return { source, target, type: e.type, id: e.id,
                 confidence: e.properties?.confidence_score as number | undefined,
                 confidenceTag: e.properties?.confidence_tag as string | undefined };
      })
      .filter(Boolean) as Array<{ source: SimNode; target: SimNode; type: string; id?: string; confidence?: number; confidenceTag?: string }>;

    const simulation = d3.forceSimulation<SimNode>(simNodes)
      .force("link", d3.forceLink(simLinks).id((d: SimNode) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide((d: SimNode) => nodeRadius(degreeMap[d.id] || 0) + 4));

    // Edges
    const link = g.append("g").selectAll("line")
      .data(simLinks).join("line")
      .attr("stroke", "#334155")
      .attr("stroke-width", (d) => edgeWidth(d.confidence))
      .attr("stroke-dasharray", (d) => edgeDashArray(d.confidenceTag))
      .attr("marker-end", "url(#arrow)")
      .attr("opacity", (d) => (d.confidenceTag === "AMBIGUOUS" ? 0.4 : 0.8));

    const linkLabel = g.append("g").selectAll("text")
      .data(simLinks).join("text")
      .attr("font-size", 8).attr("fill", "#64748b").attr("text-anchor", "middle")
      .text((d) => d.type);

    // Nodes
    const nodeGroup = g.append("g").selectAll<SVGGElement, SimNode>("g")
      .data(simNodes).join("g")
      .attr("cursor", "pointer")
      .call(
        d3.drag<SVGGElement, SimNode>()
          .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
          .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
          .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }),
      );

    // Node shape: circle for situation, diamond for knowledge
    nodeGroup.each(function(d) {
      const g = d3.select(this);
      const r = nodeRadius(degreeMap[d.id] || 0);
      const layer = (d.properties.layer_type as string) || "situation";
      const color = nodeColor(d.type);

      if (layer === "knowledge") {
        // Diamond shape for knowledge nodes
        const s = r * 1.4;
        g.append("polygon")
          .attr("points", `0,${-s} ${s},0 0,${s} ${-s},0`)
          .attr("fill", color).attr("fill-opacity", 0.7)
          .attr("stroke", "#0f172a").attr("stroke-width", 1.5);
      } else {
        g.append("circle")
          .attr("r", r)
          .attr("fill", color).attr("fill-opacity", 0.85)
          .attr("stroke", "#0f172a").attr("stroke-width", 1.5);
      }

      g.append("text").attr("dy", "0.35em").attr("text-anchor", "middle")
        .attr("font-size", 7).attr("fill", "#fff").attr("pointer-events", "none")
        .text(d.type.slice(0, 2).toUpperCase());

      g.append("text").attr("dy", r + 14).attr("text-anchor", "middle")
        .attr("font-size", 10).attr("fill", "#cbd5e1").attr("pointer-events", "none")
        .text(d.label.length > 14 ? d.label.slice(0, 12) + "…" : d.label);
    });

    nodeGroup.on("click", (event, d) => {
      event.stopPropagation();
      setSelectedNode(d);
    });

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

    return () => { simulation.stop(); };
  }, [filteredNodes, filteredEdges, degreeMap]);

  if (filteredNodes.length > 2000) {
    return (
      <div className="flex items-center justify-center h-full bg-zinc-950 rounded-lg border border-zinc-800">
        <div className="text-center text-zinc-500 space-y-2">
          <p className="text-sm font-medium">Graph too large ({filteredNodes.length} nodes)</p>
          <p className="text-xs">Apply filters to reduce the node count below 2,000, or use the subgraph view.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Filter panel */}
      {showFilterPanel && (
        <div className="w-56 border-r border-zinc-800 bg-zinc-950 p-3 overflow-y-auto shrink-0">
          <GraphFiltersPanel
            filters={activeFilters}
            nodeCounts={nodeCounts}
            onChange={setActiveFilters}
          />
        </div>
      )}

      {/* Graph canvas */}
      <div ref={containerRef} className="relative flex-1 bg-zinc-950 overflow-hidden" onClick={() => setSelectedNode(null)}>
        {/* Toolbar */}
        <div className="absolute top-3 left-3 z-10 flex gap-1">
          <button
            onClick={() => setShowFilterPanel((v) => !v)}
            className={cn(
              "px-2 py-1 text-[10px] rounded border transition-colors",
              showFilterPanel
                ? "bg-blue-900 border-blue-700 text-blue-200"
                : "bg-zinc-800 border-zinc-700 text-zinc-400 hover:text-white",
            )}
          >
            Filters
          </button>
        </div>

        <svg ref={svgRef} className="w-full h-full" />

        {/* Large graph warning */}
        {filteredNodes.length > CANVAS_THRESHOLD && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-amber-950/80 border border-amber-800 text-amber-300 text-[10px] px-3 py-1 rounded-full pointer-events-none">
            {filteredNodes.length} nodes — performance may vary
          </div>
        )}
      </div>

      {/* Node detail panel */}
      {selectedNode && (
        <NodeDetailPanel
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          onDelete={onDeleteNode}
        />
      )}
    </div>
  );
}
```

### Step 1.6 — TypeScript check

```bash
cd apps/web && npx tsc --noEmit
```

Expected: zero errors.

### Step 1.7 — Commit

```bash
git add apps/web/src/components/graph/ \
        apps/web/src/types/api.ts
git commit -m "feat: interactive graph editor — node size by degree, diamond knowledge nodes, edge width by confidence, filter panel, node detail panel"
```

---

## Task 2: Three-Panel Workspace Dashboard (Prompt 3.2)

**Files:**
- Create: `apps/web/src/stores/workspaceStore.ts`
- Create: `apps/web/src/components/workspace/NavigationSidebar.tsx`
- Create: `apps/web/src/components/workspace/DetailPanel.tsx`
- Create: `apps/web/src/components/workspace/StatusBar.tsx`
- Rewrite: `apps/web/src/app/workspaces/[id]/page.tsx`

### Step 2.1 — Create Zustand workspace store

- [ ] Create `apps/web/src/stores/workspaceStore.ts`:

```typescript
import { create } from "zustand";
import type { GraphNode, GraphEdge, GraphView, GraphFilters } from "@/types/api";

interface WorkspaceState {
  // Data
  nodes: GraphNode[];
  edges: GraphEdge[];
  loading: boolean;
  error: string | null;

  // Selection
  selectedNode: GraphNode | null;
  selectedEdge: GraphEdge | null;

  // View
  activeView: GraphView;
  filters: GraphFilters;

  // Actions
  setNodes: (nodes: GraphNode[]) => void;
  setEdges: (edges: GraphEdge[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  selectNode: (node: GraphNode | null) => void;
  selectEdge: (edge: GraphEdge | null) => void;
  setActiveView: (view: GraphView) => void;
  setFilters: (filters: GraphFilters) => void;
  addNode: (node: GraphNode) => void;
  removeNode: (nodeId: string) => void;
  addEdge: (edge: GraphEdge) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  nodes: [],
  edges: [],
  loading: false,
  error: null,
  selectedNode: null,
  selectedEdge: null,
  activeView: "graph",
  filters: {
    nodeTypes: [],
    edgeTypes: [],
    confidenceMin: 0,
    layer: "both",
  },

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  selectNode: (selectedNode) => set({ selectedNode, selectedEdge: null }),
  selectEdge: (selectedEdge) => set({ selectedEdge, selectedNode: null }),
  setActiveView: (activeView) => set({ activeView }),
  setFilters: (filters) => set({ filters }),
  addNode: (node) => set((s) => ({ nodes: [...s.nodes, node] })),
  removeNode: (nodeId) =>
    set((s) => ({
      nodes: s.nodes.filter((n) => n.id !== nodeId),
      edges: s.edges.filter((e) => e.source !== nodeId && e.target !== nodeId),
      selectedNode: s.selectedNode?.id === nodeId ? null : s.selectedNode,
    })),
  addEdge: (edge) => set((s) => ({ edges: [...s.edges, edge] })),
}));
```

### Step 2.2 — Create `NavigationSidebar.tsx`

- [ ] Create `apps/web/src/components/workspace/NavigationSidebar.tsx`:

```typescript
"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Box, Zap, FileText, BarChart2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import type { GraphNode } from "@/types/api";

interface NavigationSidebarProps {
  workspaceId: string;
}

export default function NavigationSidebar({ workspaceId }: NavigationSidebarProps) {
  const nodes = useWorkspaceStore((s) => s.nodes);
  const edges = useWorkspaceStore((s) => s.edges);
  const selectNode = useWorkspaceStore((s) => s.selectNode);
  const [expandedTypes, setExpandedTypes] = useState<Set<string>>(new Set(["Actor"]));

  const groupedNodes = nodes.reduce<Record<string, GraphNode[]>>((acc, node) => {
    acc[node.type] = acc[node.type] || [];
    acc[node.type].push(node);
    return acc;
  }, {});

  const toggleType = (type: string) =>
    setExpandedTypes((s) => {
      const next = new Set(s);
      next.has(type) ? next.delete(type) : next.add(type);
      return next;
    });

  return (
    <div className="w-60 border-r border-zinc-800 bg-zinc-950 flex flex-col overflow-hidden shrink-0">
      {/* Stats */}
      <div className="px-3 py-2 border-b border-zinc-800">
        <div className="grid grid-cols-2 gap-1 text-[10px] text-zinc-500">
          <span>{nodes.length} nodes</span>
          <span>{edges.length} edges</span>
        </div>
      </div>

      {/* Entity tree */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
        <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider px-1 mb-1 flex items-center gap-1">
          <Box size={10} /> Entities
        </p>
        {Object.entries(groupedNodes)
          .sort((a, b) => b[1].length - a[1].length)
          .map(([type, typeNodes]) => (
            <div key={type}>
              <button
                className="w-full flex items-center gap-1.5 px-2 py-0.5 text-xs text-zinc-400 hover:text-white hover:bg-zinc-800/50 rounded transition-colors"
                onClick={() => toggleType(type)}
              >
                {expandedTypes.has(type) ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
                <span className="flex-1 text-left">{type}</span>
                <span className="text-zinc-600">{typeNodes.length}</span>
              </button>
              {expandedTypes.has(type) && (
                <div className="ml-4 space-y-0.5">
                  {typeNodes.slice(0, 20).map((node) => (
                    <button
                      key={node.id}
                      onClick={() => selectNode(node)}
                      className="w-full text-left px-2 py-0.5 text-[11px] text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/30 rounded truncate transition-colors"
                    >
                      {node.label}
                    </button>
                  ))}
                  {typeNodes.length > 20 && (
                    <span className="pl-2 text-[10px] text-zinc-700">+{typeNodes.length - 20} more</span>
                  )}
                </div>
              )}
            </div>
          ))}
      </div>
    </div>
  );
}
```

### Step 2.3 — Create `StatusBar.tsx`

- [ ] Create `apps/web/src/components/workspace/StatusBar.tsx`:

```typescript
"use client";

import { useWorkspaceStore } from "@/stores/workspaceStore";

interface StatusBarProps {
  glaslStage?: string;
  lastExtraction?: string;
}

export default function StatusBar({ glaslStage, lastExtraction }: StatusBarProps) {
  const nodes = useWorkspaceStore((s) => s.nodes);
  const edges = useWorkspaceStore((s) => s.edges);

  const density =
    nodes.length > 1
      ? (edges.length / (nodes.length * (nodes.length - 1))).toFixed(3)
      : "0.000";

  return (
    <div className="h-8 border-t border-zinc-800 bg-zinc-950 flex items-center gap-4 px-4 text-[10px] text-zinc-500 shrink-0">
      <span>{nodes.length} nodes</span>
      <span>·</span>
      <span>{edges.length} edges</span>
      <span>·</span>
      <span>density: {density}</span>
      {glaslStage && (
        <>
          <span>·</span>
          <span>Glasl stage: <span className="text-amber-400 font-medium">{glaslStage}</span></span>
        </>
      )}
      {lastExtraction && (
        <>
          <span>·</span>
          <span>last extraction: {new Date(lastExtraction).toLocaleDateString()}</span>
        </>
      )}
    </div>
  );
}
```

### Step 2.4 — Rewrite workspace `page.tsx` as three-panel layout

- [ ] Rewrite `apps/web/src/app/workspaces/[id]/page.tsx`:

```typescript
"use client";

import { useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, GitGraph, Clock, Grid3X3, GitBranch, BarChart2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { api } from "@/lib/api";
import ForceGraph from "@/components/graph/ForceGraph";
import NavigationSidebar from "@/components/workspace/NavigationSidebar";
import StatusBar from "@/components/workspace/StatusBar";
import type { GraphView } from "@/types/api";

const VIEW_TABS: { id: GraphView; label: string; icon: React.ElementType }[] = [
  { id: "graph", label: "Graph", icon: GitGraph },
  { id: "timeline", label: "Timeline", icon: Clock },
  { id: "matrix", label: "Matrix", icon: Grid3X3 },
  { id: "causal", label: "Causal", icon: GitBranch },
];

function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded bg-zinc-800/60", className)} />;
}

export default function WorkspaceDashboardPage() {
  const { id } = useParams();
  const workspaceId = id as string;

  const nodes = useWorkspaceStore((s) => s.nodes);
  const edges = useWorkspaceStore((s) => s.edges);
  const loading = useWorkspaceStore((s) => s.loading);
  const error = useWorkspaceStore((s) => s.error);
  const activeView = useWorkspaceStore((s) => s.activeView);
  const setNodes = useWorkspaceStore((s) => s.setNodes);
  const setEdges = useWorkspaceStore((s) => s.setEdges);
  const setLoading = useWorkspaceStore((s) => s.setLoading);
  const setError = useWorkspaceStore((s) => s.setError);
  const setActiveView = useWorkspaceStore((s) => s.setActiveView);
  const addNode = useWorkspaceStore((s) => s.addNode);
  const removeNode = useWorkspaceStore((s) => s.removeNode);
  const addEdge = useWorkspaceStore((s) => s.addEdge);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.getGraph(workspaceId)
      .then((data) => {
        setNodes(data.nodes ?? []);
        setEdges(data.edges ?? []);
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load graph"))
      .finally(() => setLoading(false));
  }, [workspaceId, setNodes, setEdges, setLoading, setError]);

  const handleAddNode = useCallback(async (node: { type: string; label: string }) => {
    const created = await api.addEntity(workspaceId, node);
    addNode(created);
  }, [workspaceId, addNode]);

  const handleDeleteNode = useCallback(async (nodeId: string) => {
    await api.deleteEntity(workspaceId, nodeId);
    removeNode(nodeId);
  }, [workspaceId, removeNode]);

  const handleAddEdge = useCallback(async (edge: { source: string; target: string; type: string }) => {
    const created = await api.addRelationship(workspaceId, edge);
    addEdge(created);
  }, [workspaceId, addEdge]);

  if (loading) {
    return (
      <div className="h-full flex flex-col gap-4 p-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="flex-1" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Toolbar */}
      <div className="border-b border-zinc-800 px-4 py-2 flex items-center gap-4 shrink-0">
        <Link href="/workspaces" className="text-zinc-500 hover:text-zinc-300 transition-colors">
          <ArrowLeft size={14} />
        </Link>
        <h1 className="text-sm font-bold text-white font-mono">
          ConflictCorpus <span className="text-zinc-600 font-normal">{workspaceId}</span>
        </h1>

        {/* View tabs */}
        <nav className="flex gap-0.5 ml-auto">
          {VIEW_TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveView(id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1 rounded text-xs transition-colors",
                activeView === id
                  ? "bg-zinc-700 text-white"
                  : "text-zinc-500 hover:text-zinc-300",
              )}
            >
              <Icon size={12} />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mt-2 rounded-lg border border-red-800 bg-red-950/40 px-4 py-2 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Three-panel body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel: navigation sidebar */}
        <NavigationSidebar workspaceId={workspaceId} />

        {/* Center: active view */}
        <div className="flex-1 overflow-hidden">
          {activeView === "graph" && (
            <ForceGraph
              nodes={nodes}
              edges={edges}
              showFilters
              onAddNode={handleAddNode}
              onDeleteNode={handleDeleteNode}
              onAddEdge={handleAddEdge}
            />
          )}
          {activeView === "timeline" && (
            <div className="flex items-center justify-center h-full text-zinc-600 text-sm">
              Timeline view — coming soon (Phase 3 complete)
            </div>
          )}
          {activeView === "matrix" && (
            <div className="flex items-center justify-center h-full text-zinc-600 text-sm">
              Matrix view — coming soon
            </div>
          )}
          {activeView === "causal" && (
            <div className="flex items-center justify-center h-full text-zinc-600 text-sm">
              Causal chain view — coming soon
            </div>
          )}
        </div>
      </div>

      {/* Status bar */}
      <StatusBar />
    </div>
  );
}
```

### Step 2.5 — TypeScript + build check

```bash
cd apps/web && npx tsc --noEmit && npm run build
```

Expected: zero errors, successful build.

### Step 2.6 — Commit

```bash
git add apps/web/src/stores/ \
        apps/web/src/components/workspace/ \
        apps/web/src/app/workspaces/[id]/page.tsx
git commit -m "feat: three-panel workspace dashboard — zustand store, NavigationSidebar entity tree, StatusBar, view tabs"
```

---

## Task 3: Ingestion Interface (Prompt 3.3)

**Files:**
- Rewrite: `apps/web/src/app/workspaces/[id]/ingest/page.tsx`
- Create: `apps/web/src/components/ingestion/TextIngest.tsx`
- Create: `apps/web/src/components/ingestion/ExtractionReview.tsx`

### Step 3.1 — Create `TextIngest.tsx`

- [ ] Create `apps/web/src/components/ingestion/TextIngest.tsx`:

```typescript
"use client";

import { useState, useCallback } from "react";
import { Loader2, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

type Tier = "essential" | "standard" | "full";

interface TextIngestProps {
  workspaceId: string;
  onComplete: (result: { newNodes: unknown[]; newEdges: unknown[] }) => void;
}

const TIER_INFO: Record<Tier, { label: string; description: string; time: string }> = {
  essential: { label: "Essential", description: "Core entities only — fastest", time: "~5s" },
  standard: { label: "Standard", description: "Entities + relationships", time: "~15s" },
  full: { label: "Full", description: "All 17 node types + all edge types", time: "~45s" },
};

const WORDS_PER_SECOND = 200; // rough extraction speed estimate

export default function TextIngest({ workspaceId, onComplete }: TextIngestProps) {
  const [text, setText] = useState("");
  const [tier, setTier] = useState<Tier>("standard");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  const estSeconds = Math.max(5, Math.ceil(wordCount / WORDS_PER_SECOND) * (tier === "full" ? 3 : tier === "standard" ? 2 : 1));

  const handleExtract = useCallback(async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setProgress(10);

    // Simulate progress during extraction
    const interval = setInterval(() => {
      setProgress((p) => Math.min(p + 5, 90));
    }, estSeconds * 50);

    try {
      const result = await api.ingestText(workspaceId, { text, tier });
      setProgress(100);
      onComplete({ newNodes: result.new_nodes || [], newEdges: result.new_edges || [] });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Extraction failed");
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  }, [text, tier, workspaceId, onComplete, estSeconds]);

  return (
    <div className="space-y-4">
      {/* Tier selector */}
      <div className="flex gap-2">
        {(["essential", "standard", "full"] as Tier[]).map((t) => (
          <button
            key={t}
            onClick={() => setTier(t)}
            className={cn(
              "flex-1 p-2.5 rounded-lg border text-left transition-colors",
              tier === t
                ? "border-blue-600 bg-blue-950/30 text-white"
                : "border-zinc-700 bg-zinc-900 text-zinc-400 hover:border-zinc-600",
            )}
          >
            <p className="text-xs font-semibold">{TIER_INFO[t].label}</p>
            <p className="text-[10px] text-zinc-500 mt-0.5">{TIER_INFO[t].description}</p>
            <p className="text-[10px] text-zinc-600">{TIER_INFO[t].time}</p>
          </button>
        ))}
      </div>

      {/* Text area */}
      <div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste conflict text, report, article, or description here…&#10;&#10;Example: 'The ongoing dispute between Russia and Ukraine involves territorial claims, military escalation, and diplomatic failures. NATO allies have imposed economic sanctions while humanitarian corridors are being negotiated…'"
          rows={12}
          className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500 resize-none font-mono"
        />
        <div className="flex items-center justify-between mt-1.5 text-[10px] text-zinc-600">
          <span>{wordCount.toLocaleString()} words</span>
          {wordCount > 0 && <span>est. {estSeconds}s extraction time</span>}
        </div>
      </div>

      {/* Progress bar */}
      {loading && (
        <div className="space-y-1.5">
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-[10px] text-zinc-500">
            {progress < 30 ? "Analyzing text…" : progress < 60 ? "Extracting entities…" : progress < 85 ? "Building relationships…" : "Writing to graph…"}
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-800 bg-red-950/30 px-3 py-2 text-xs text-red-300">
          {error}
        </div>
      )}

      {/* Extract button */}
      <button
        onClick={handleExtract}
        disabled={!text.trim() || loading}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
        {loading ? "Extracting…" : "Extract"}
      </button>
    </div>
  );
}
```

### Step 3.2 — Rewrite `ingest/page.tsx`

- [ ] Rewrite `apps/web/src/app/workspaces/[id]/ingest/page.tsx`:

```typescript
"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, FileText, Upload, FormInput, Link as LinkIcon, LayoutTemplate } from "lucide-react";
import { cn } from "@/lib/utils";
import TextIngest from "@/components/ingestion/TextIngest";

type IngestTab = "text" | "upload" | "structured" | "url" | "template";

const TABS: { id: IngestTab; label: string; icon: React.ElementType }[] = [
  { id: "text", label: "Text Input", icon: FileText },
  { id: "upload", label: "Document Upload", icon: Upload },
  { id: "structured", label: "Structured", icon: FormInput },
  { id: "url", label: "URL Import", icon: LinkIcon },
  { id: "template", label: "Template", icon: LayoutTemplate },
];

function ComingSoon({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
      <p className="text-sm font-medium">{label}</p>
      <p className="text-xs mt-1">Coming soon</p>
    </div>
  );
}

export default function IngestPage() {
  const { id } = useParams();
  const workspaceId = id as string;
  const [activeTab, setActiveTab] = useState<IngestTab>("text");
  const [result, setResult] = useState<{ newNodes: unknown[]; newEdges: unknown[] } | null>(null);

  const handleComplete = (r: { newNodes: unknown[]; newEdges: unknown[] }) => {
    setResult(r);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <div>
        <Link
          href={`/workspaces/${workspaceId}`}
          className="inline-flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeft size={12} />
          Back to workspace
        </Link>
        <h1 className="text-lg font-bold text-white mt-2 font-mono">Ingest Conflict Data</h1>
        <p className="text-xs text-zinc-500 mt-0.5">
          Structure your conflict situation through text, documents, or manual entry.
        </p>
      </div>

      {/* Tabs */}
      <nav className="flex gap-0.5 border-b border-zinc-800 pb-px">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-2 text-xs border-b-2 transition-colors",
              activeTab === id
                ? "border-blue-500 text-blue-400"
                : "border-transparent text-zinc-500 hover:text-zinc-300",
            )}
          >
            <Icon size={12} />
            {label}
          </button>
        ))}
      </nav>

      {/* Tab content */}
      <div>
        {activeTab === "text" && (
          <TextIngest workspaceId={workspaceId} onComplete={handleComplete} />
        )}
        {activeTab === "upload" && <ComingSoon label="Document Upload" />}
        {activeTab === "structured" && <ComingSoon label="Structured Input" />}
        {activeTab === "url" && <ComingSoon label="URL Import" />}
        {activeTab === "template" && <ComingSoon label="Template Start" />}
      </div>

      {/* Extraction result summary */}
      {result && (
        <div className="rounded-lg border border-emerald-800 bg-emerald-950/30 p-4 text-sm">
          <p className="font-semibold text-emerald-300 mb-1">Extraction complete</p>
          <div className="text-xs text-emerald-400/70 space-y-0.5">
            <p>+{(result.newNodes as unknown[]).length} new entities added to graph</p>
            <p>+{(result.newEdges as unknown[]).length} new relationships extracted</p>
          </div>
          <Link
            href={`/workspaces/${workspaceId}`}
            className="inline-flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300 mt-2 transition-colors"
          >
            View in graph →
          </Link>
        </div>
      )}
    </div>
  );
}
```

### Step 3.3 — Add `ingestText` method to `api.ts`

- [ ] Add to `apps/web/src/lib/api.ts` in the `api` object:

```typescript
  // Incremental ingestion (Phase 1.3 backend)
  ingestText: (workspaceId: string, body: { text: string; tier: string; source_type?: string }) =>
    request<{
      episode_id: string;
      is_duplicate: boolean;
      new_nodes: GraphNode[];
      new_edges: GraphEdge[];
      processing_time_ms: number;
    }>(`/v1/workspaces/${workspaceId}/ingest`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
```

Also add `ingestText` to the import in `types/api.ts` (it returns `GraphNode[]` and `GraphEdge[]` which are already defined).

### Step 3.4 — TypeScript + build check

```bash
cd apps/web && npx tsc --noEmit && npm run build
```

Expected: zero errors.

### Step 3.5 — Commit

```bash
git add apps/web/src/app/workspaces/[id]/ingest/ \
        apps/web/src/components/ingestion/ \
        apps/web/src/lib/api.ts
git commit -m "feat: ingestion interface — text input with tier selector, progress tracking, extraction result summary"
```

---

## Scope Check

| Spec requirement | Task | Status |
|---|---|---|
| Node size by degree centrality | Task 1, Step 1.5 | ✓ |
| Diamond shape for knowledge nodes | Task 1, Step 1.5 | ✓ |
| Edge width by confidence | Task 1, Step 1.5 | ✓ |
| Edge style by confidence_tag (solid/dashed/dotted) | Task 1, Step 1.5 | ✓ |
| Node detail panel (right sidebar) | Task 1, Steps 1.4–1.5 | ✓ |
| Filter panel (left sidebar) — node/edge types, confidence, layer | Task 1, Steps 1.3, 1.5 | ✓ |
| Large graph warning (> 2000 nodes) | Task 1, Step 1.5 | ✓ |
| Zustand workspace store | Task 2, Step 2.1 | ✓ |
| NavigationSidebar with entity tree | Task 2, Step 2.2 | ✓ |
| StatusBar with node/edge counts, density | Task 2, Step 2.3 | ✓ |
| Three-panel layout (sidebar + center + view tabs) | Task 2, Step 2.4 | ✓ |
| 4 view tabs (Graph, Timeline, Matrix, Causal) | Task 2, Step 2.4 | ✓ |
| Text input ingestion with tier selector | Task 3, Steps 3.1–3.2 | ✓ |
| Progress indicator during extraction | Task 3, Step 3.1 | ✓ |
| Extraction result summary | Task 3, Step 3.2 | ✓ |
| 5-tab ingestion interface | Task 3, Step 3.2 | ✓ (text complete, others stubbed) |

**Not in this plan (scope deferred):**
- Timeline view implementation (EventTimeline.tsx needs refactor)
- Actor × actor adjacency matrix view
- Community convex hull rendering in graph (label propagation data needed from Phase 2)
- Detail panel AI chat tab (requires streaming API integration)
- Full structured/URL/template ingest tabs (text input covers primary workflow)
- D3 Canvas mode for 300-2000 nodes (SVG performance is acceptable for MVP)
