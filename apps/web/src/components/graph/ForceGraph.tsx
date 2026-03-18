"use client";

import { useRef, useEffect, useCallback } from "react";
import * as d3 from "d3";
import type { GraphNode, GraphLink, GraphData } from "@/types/graph";
import { NODE_COLORS } from "@/lib/utils";

interface Props {
  data: GraphData;
  width: number;
  height: number;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (link: GraphLink) => void;
  onNodeDoubleClick?: (node: GraphNode) => void;
  selectedNodeId?: string | null;
}

export default function ForceGraph({ data, width, height, onNodeClick, onEdgeClick, onNodeDoubleClick, selectedNodeId }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);

  const render = useCallback(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const g = svg.append("g");

    // Zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on("zoom", (event) => g.attr("transform", event.transform));
    svg.call(zoom);

    // Simulation
    const simulation = d3.forceSimulation<GraphNode>(data.nodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(data.links).id((d) => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(20));

    simulationRef.current = simulation;

    // Links
    const link = g.append("g")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke", "#334155")
      .attr("stroke-width", (d) => Math.max(1, d.weight * 2))
      .attr("stroke-opacity", 0.6)
      .style("cursor", "pointer")
      .on("click", (_event, d) => onEdgeClick?.(d));

    // Nodes
    const node = g.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .join("circle")
      .attr("r", (d) => Math.max(6, (d.properties.centrality as number || 0.5) * 16))
      .attr("fill", (d) => NODE_COLORS[d.node_type] || "#94a3b8")
      .attr("stroke", (d) => d.id === selectedNodeId ? "#f1f5f9" : "transparent")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .on("click", (_event, d) => onNodeClick?.(d))
      .on("dblclick", (_event, d) => onNodeDoubleClick?.(d))
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .call(d3.drag<any, GraphNode>()
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

    // Labels
    const label = g.append("g")
      .selectAll("text")
      .data(data.nodes)
      .join("text")
      .text((d) => d.name)
      .attr("font-size", 10)
      .attr("fill", "#94a3b8")
      .attr("dx", 12)
      .attr("dy", 4)
      .style("pointer-events", "none");

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as GraphNode).x!)
        .attr("y1", (d) => (d.source as GraphNode).y!)
        .attr("x2", (d) => (d.target as GraphNode).x!)
        .attr("y2", (d) => (d.target as GraphNode).y!);
      node
        .attr("cx", (d) => d.x!)
        .attr("cy", (d) => d.y!);
      label
        .attr("x", (d) => d.x!)
        .attr("y", (d) => d.y!);
    });

    return () => simulation.stop();
  }, [data, width, height, onNodeClick, onEdgeClick, onNodeDoubleClick, selectedNodeId]);

  useEffect(() => {
    render();
    return () => { simulationRef.current?.stop(); };
  }, [render]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="bg-background rounded-lg"
    />
  );
}
