"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import * as d3 from "d3";
import type { GraphNode, GraphLink, GraphData } from "@/types/graph";
import { NODE_COLORS } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/*  Edge color palette by edge_type                                    */
/* ------------------------------------------------------------------ */

const EDGE_COLORS: Record<string, string> = {
  CAUSED: "#ef4444",
  PARTY_TO: "#3b82f6",
  HAS_INTEREST: "#22c55e",
  HAS_POWER_OVER: "#a855f7",
  EXPERIENCES: "#f43f5e",
  TRUSTS: "#8b5cf6",
  ALLIED_WITH: "#06b6d4",
  OPPOSED_TO: "#ef4444",
  VIOLATES: "#f97316",
  PART_OF: "#64748b",
  PARTICIPATES_IN: "#3b82f6",
  MEMBER_OF: "#64748b",
  GOVERNED_BY: "#f97316",
  RESOLVED_THROUGH: "#06b6d4",
  PRODUCES: "#10b981",
  PROMOTES: "#ec4899",
  ABOUT: "#64748b",
  EVIDENCED_BY: "#94a3b8",
  AT_LOCATION: "#78716c",
  PERFORMED: "#eab308",
  TARGETED: "#ef4444",
  HAS_TRUST_STATE: "#8b5cf6",
  HELD_BY: "#a855f7",
  MOTIVATED: "#f43f5e",
  GOVERNS: "#f97316",
  WITHIN: "#78716c",
};

const DEFAULT_EDGE_COLOR = "#475569";

/* ------------------------------------------------------------------ */
/*  Link distance by edge type                                         */
/* ------------------------------------------------------------------ */

const LINK_DISTANCES: Record<string, number> = {
  CAUSED: 120,
  PARTY_TO: 100,
  PARTICIPATES_IN: 100,
  MEMBER_OF: 100,
};
const DEFAULT_LINK_DISTANCE = 80;

/* ------------------------------------------------------------------ */
/*  Readable node type label                                           */
/* ------------------------------------------------------------------ */

function nodeTypeLabel(t: string): string {
  return t
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

/* ------------------------------------------------------------------ */
/*  Tooltip types                                                      */
/* ------------------------------------------------------------------ */

interface TooltipInfo {
  x: number;
  y: number;
  node?: GraphNode;
  link?: GraphLink;
}

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */

interface Props {
  data: GraphData;
  width: number;
  height: number;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (link: GraphLink) => void;
  onNodeDoubleClick?: (node: GraphNode) => void;
  selectedNodeId?: string | null;
  highlightNodeIds?: string[];
  highlightEdgeIds?: string[];
}

export default function ForceGraph({
  data,
  width,
  height,
  onNodeClick,
  onEdgeClick,
  onNodeDoubleClick,
  selectedNodeId,
  highlightNodeIds = [],
  highlightEdgeIds = [],
}: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);
  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);

  const render = useCallback(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const highlightedNodes = new Set(highlightNodeIds);
    const highlightedEdges = new Set(highlightEdgeIds);
    const hasHighlights = highlightedNodes.size > 0 || highlightedEdges.size > 0;

    /* ---- Defs: arrow markers & glow filter ---- */
    const defs = svg.append("defs");

    // Create an arrowhead marker per edge color
    const usedColors = new Set<string>();
    for (const link of data.links) {
      usedColors.add(EDGE_COLORS[link.edge_type] || DEFAULT_EDGE_COLOR);
    }
    usedColors.forEach((color) => {
      const markerId = `arrow-${color.replace("#", "")}`;
      defs
        .append("marker")
        .attr("id", markerId)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-4L8,0L0,4")
        .attr("fill", color)
        .attr("fill-opacity", 0.7);
    });

    // Glow filter for selected node
    const glow = defs.append("filter").attr("id", "glow");
    glow
      .append("feGaussianBlur")
      .attr("stdDeviation", "4")
      .attr("result", "coloredBlur");
    const glowMerge = glow.append("feMerge");
    glowMerge.append("feMergeNode").attr("in", "coloredBlur");
    glowMerge.append("feMergeNode").attr("in", "SourceGraphic");

    const g = svg.append("g");

    // Track current zoom scale for edge label visibility
    let currentScale = 1;

    /* ---- Zoom ---- */
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
        currentScale = event.transform.k;
        // Toggle edge label visibility based on zoom
        edgeLabels.attr("opacity", currentScale > 0.8 ? 0.85 : 0);
      });
    svg.call(zoom);

    /* ---- Simulation ---- */
    const simulation = d3
      .forceSimulation<GraphNode>(data.nodes)
      .force(
        "link",
        d3
          .forceLink<GraphNode, GraphLink>(data.links)
          .id((d) => d.id)
          .distance((d) => LINK_DISTANCES[d.edge_type] || DEFAULT_LINK_DISTANCE)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force(
        "collision",
        d3.forceCollide<GraphNode>().radius((d) => {
          const centrality = (d.properties.centrality as number) || 0.5;
          return Math.max(8, Math.min(20, centrality * 24)) + 6;
        })
      );

    simulationRef.current = simulation;

    /* ---- Links (lines) ---- */
    const link = g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke", (d) => EDGE_COLORS[d.edge_type] || DEFAULT_EDGE_COLOR)
      .attr("stroke-width", (d) =>
        Math.max(1, d.weight * (highlightedEdges.has(d.id) ? 4 : 2.5))
      )
      .attr("stroke-opacity", (d) => {
        if (!hasHighlights) return 0.5;
        return highlightedEdges.has(d.id) ? 0.9 : 0.16;
      })
      .attr("marker-end", (d) => {
        const c = EDGE_COLORS[d.edge_type] || DEFAULT_EDGE_COLOR;
        return `url(#arrow-${c.replace("#", "")})`;
      })
      .style("cursor", "pointer")
      .on("click", (_event, d) => onEdgeClick?.(d))
      .on("mouseenter", (event, d) => {
        const rect = svgRef.current!.getBoundingClientRect();
        setTooltip({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
          link: d,
        });
      })
      .on("mouseleave", () => setTooltip((prev) => (prev?.link ? null : prev)));

    /* ---- Edge labels ---- */
    const edgeLabels = g
      .append("g")
      .attr("class", "edge-labels")
      .selectAll("text")
      .data(data.links)
      .join("text")
      .text((d) => d.edge_type)
      .attr("font-size", "8px")
      .attr("fill", "#64748b")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("opacity", currentScale > 0.8 ? 0.85 : 0)
      .style("pointer-events", "none")
      .style("user-select", "none");

    /* ---- Nodes (circles) ---- */
    const nodeRadius = (d: GraphNode) => {
      const centrality = (d.properties.centrality as number) || 0.5;
      return Math.max(8, Math.min(20, centrality * 24));
    };

    const node = g
      .append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(data.nodes)
      .join("circle")
      .attr("r", nodeRadius)
      .attr("fill", (d) => NODE_COLORS[d.node_type] || "#94a3b8")
      .attr("opacity", (d) => {
        if (!hasHighlights) return 1;
        return highlightedNodes.has(d.id) ? 1 : 0.35;
      })
      .attr("stroke", (d) => {
        if (d.id === selectedNodeId || highlightedNodes.has(d.id)) return "#f1f5f9";
        return "rgba(255,255,255,0.1)";
      })
      .attr("stroke-width", (d) => (d.id === selectedNodeId || highlightedNodes.has(d.id) ? 3 : 1))
      .attr("filter", (d) => (d.id === selectedNodeId || highlightedNodes.has(d.id) ? "url(#glow)" : "none"))
      .style("cursor", "pointer")
      .on("click", (_event, d) => onNodeClick?.(d))
      .on("dblclick", (_event, d) => onNodeDoubleClick?.(d))
      .on("mouseenter", (event, d) => {
        const rect = svgRef.current!.getBoundingClientRect();
        setTooltip({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
          node: d,
        });
      })
      .on("mouseleave", () => setTooltip((prev) => (prev?.node ? null : prev)))
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .call(
        d3
          .drag<any, GraphNode>()
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
          })
      );

    /* ---- Node name labels ---- */
    const nameLabels = g
      .append("g")
      .attr("class", "node-labels")
      .selectAll("text")
      .data(data.nodes)
      .join("text")
      .text((d) => (d.name.length > 18 ? d.name.slice(0, 16) + ".." : d.name))
      .attr("font-size", "10px")
      .attr("font-weight", "600")
      .attr("fill", "#cbd5e1")
      .attr("dx", (d) => nodeRadius(d) + 6)
      .attr("dy", -2)
      .style("pointer-events", "none")
      .style("user-select", "none");

    /* ---- Node type badge labels ---- */
    const typeLabels = g
      .append("g")
      .attr("class", "type-labels")
      .selectAll("text")
      .data(data.nodes)
      .join("text")
      .text((d) => nodeTypeLabel(d.node_type))
      .attr("font-size", "7px")
      .attr("fill", "#64748b")
      .attr("dx", (d) => nodeRadius(d) + 6)
      .attr("dy", 9)
      .style("pointer-events", "none")
      .style("user-select", "none");

    /* ---- Tick ---- */
    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as GraphNode).x!)
        .attr("y1", (d) => (d.source as GraphNode).y!)
        .attr("x2", (d) => (d.target as GraphNode).x!)
        .attr("y2", (d) => (d.target as GraphNode).y!);

      // Edge labels — position at midpoint, rotated to follow link angle
      edgeLabels
        .attr("x", (d) => {
          const sx = (d.source as GraphNode).x!;
          const tx = (d.target as GraphNode).x!;
          return (sx + tx) / 2;
        })
        .attr("y", (d) => {
          const sy = (d.source as GraphNode).y!;
          const ty = (d.target as GraphNode).y!;
          return (sy + ty) / 2;
        })
        .attr("transform", (d) => {
          const sx = (d.source as GraphNode).x!;
          const sy = (d.source as GraphNode).y!;
          const tx = (d.target as GraphNode).x!;
          const ty = (d.target as GraphNode).y!;
          const mx = (sx + tx) / 2;
          const my = (sy + ty) / 2;
          let angle = (Math.atan2(ty - sy, tx - sx) * 180) / Math.PI;
          // Keep text readable (not upside down)
          if (angle > 90) angle -= 180;
          if (angle < -90) angle += 180;
          return `rotate(${angle},${mx},${my})`;
        });

      node.attr("cx", (d) => d.x!).attr("cy", (d) => d.y!);

      nameLabels.attr("x", (d) => d.x!).attr("y", (d) => d.y!);
      typeLabels.attr("x", (d) => d.x!).attr("y", (d) => d.y!);
    });

    // Smooth initial render: start with low alpha and ramp up
    simulation.alpha(1).restart();

    return () => simulation.stop();
  }, [
    data,
    width,
    height,
    onNodeClick,
    onEdgeClick,
    onNodeDoubleClick,
    selectedNodeId,
    highlightNodeIds,
    highlightEdgeIds,
  ]);

  useEffect(() => {
    render();
    return () => {
      simulationRef.current?.stop();
    };
  }, [render]);

  /* ---- Tooltip rendering helpers ---- */
  const renderNodeTooltip = (n: GraphNode) => {
    const props = n.properties;
    const entries: [string, string][] = [];
    if (props.confidence !== undefined)
      entries.push(["Confidence", `${Math.round(Number(props.confidence) * 100)}%`]);
    if (props.severity !== undefined)
      entries.push(["Severity", String(props.severity)]);
    if (props.glasl_stage !== undefined)
      entries.push(["Glasl Stage", String(props.glasl_stage)]);
    if (props.occurred_at !== undefined)
      entries.push(["Occurred", String(props.occurred_at)]);
    if (props.salience !== undefined)
      entries.push(["Salience", String(props.salience)]);
    if (props.intensity !== undefined)
      entries.push(["Intensity", String(props.intensity)]);
    if (props.valence !== undefined)
      entries.push(["Valence", String(props.valence)]);
    if (props.magnitude !== undefined)
      entries.push(["Magnitude", String(props.magnitude)]);
    if (props.overall !== undefined)
      entries.push(["Overall", String(props.overall)]);
    if (props.basis !== undefined) entries.push(["Basis", String(props.basis)]);
    if (props.reliability !== undefined)
      entries.push(["Reliability", String(props.reliability)]);
    if (props.status !== undefined) entries.push(["Status", String(props.status)]);
    if (props.priority !== undefined)
      entries.push(["Priority", String(props.priority)]);
    if (props.actor_type !== undefined)
      entries.push(["Actor Type", String(props.actor_type)]);
    if (props.role_title !== undefined)
      entries.push(["Role", String(props.role_title)]);

    return (
      <div
        className="absolute z-50 pointer-events-none"
        style={{ left: tooltip!.x + 14, top: tooltip!.y - 10 }}
      >
        <div className="bg-gray-900/95 border border-gray-700 rounded-lg px-3 py-2.5 shadow-xl max-w-[240px]">
          <div className="text-xs font-semibold text-gray-100 mb-1">{n.name}</div>
          <div className="flex items-center gap-1.5 mb-1.5">
            <span
              className="w-2 h-2 rounded-full shrink-0"
              style={{ backgroundColor: NODE_COLORS[n.node_type] || "#94a3b8" }}
            />
            <span className="text-[10px] text-gray-400 capitalize">
              {nodeTypeLabel(n.node_type)}
            </span>
          </div>
          {entries.length > 0 && (
            <div className="border-t border-gray-700 pt-1.5 space-y-0.5">
              {entries.map(([k, v]) => (
                <div key={k} className="flex justify-between gap-3 text-[10px]">
                  <span className="text-gray-500">{k}</span>
                  <span className="text-gray-300 font-mono">{v}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderLinkTooltip = (l: GraphLink) => {
    return (
      <div
        className="absolute z-50 pointer-events-none"
        style={{ left: tooltip!.x + 14, top: tooltip!.y - 10 }}
      >
        <div className="bg-gray-900/95 border border-gray-700 rounded-lg px-3 py-2 shadow-xl max-w-[200px]">
          <div className="flex items-center gap-1.5 mb-1">
            <span
              className="w-2 h-2 rounded-full shrink-0"
              style={{
                backgroundColor: EDGE_COLORS[l.edge_type] || DEFAULT_EDGE_COLOR,
              }}
            />
            <span className="text-xs font-semibold text-gray-100">
              {l.edge_type}
            </span>
          </div>
          <div className="space-y-0.5">
            <div className="flex justify-between gap-3 text-[10px]">
              <span className="text-gray-500">Weight</span>
              <span className="text-gray-300 font-mono">{l.weight}</span>
            </div>
            <div className="flex justify-between gap-3 text-[10px]">
              <span className="text-gray-500">Confidence</span>
              <span className="text-gray-300 font-mono">
                {Math.round(l.confidence * 100)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="relative" style={{ width, height }}>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="bg-background rounded-lg"
      />
      {tooltip?.node && renderNodeTooltip(tooltip.node)}
      {tooltip?.link && renderLinkTooltip(tooltip.link)}
    </div>
  );
}
