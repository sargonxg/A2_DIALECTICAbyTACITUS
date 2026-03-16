"use client";

import { useRef, useEffect } from "react";
import * as d3 from "d3";
import { NODE_COLORS } from "@/lib/utils";

interface TimelineEvent {
  id: string;
  name: string;
  occurred_at: string;
  event_type: string;
  severity: number;
  actor_id?: string;
}

interface Props {
  events: TimelineEvent[];
  width: number;
  height: number;
  onEventClick?: (event: TimelineEvent) => void;
}

export default function EventTimeline({ events, width, height, onEventClick }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !events.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 20, bottom: 40, left: 20 };
    const w = width - margin.left - margin.right;
    const h = height - margin.top - margin.bottom;

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const dates = events.map((e) => new Date(e.occurred_at));
    const xScale = d3.scaleTime().domain(d3.extent(dates) as [Date, Date]).range([0, w]);

    // Axis
    g.append("g")
      .attr("transform", `translate(0,${h})`)
      .call(d3.axisBottom(xScale).ticks(8))
      .selectAll("text")
      .attr("fill", "#94a3b8")
      .style("font-size", "10px");
    g.selectAll(".domain, .tick line").attr("stroke", "#334155");

    // Timeline line
    g.append("line")
      .attr("x1", 0).attr("y1", h / 2)
      .attr("x2", w).attr("y2", h / 2)
      .attr("stroke", "#334155").attr("stroke-width", 1);

    // Events
    g.selectAll("circle")
      .data(events)
      .join("circle")
      .attr("cx", (d) => xScale(new Date(d.occurred_at)))
      .attr("cy", h / 2)
      .attr("r", (d) => Math.max(4, d.severity * 10))
      .attr("fill", (d) => NODE_COLORS[d.event_type] || "#eab308")
      .attr("fill-opacity", 0.8)
      .style("cursor", "pointer")
      .on("click", (_event, d) => onEventClick?.(d));

    // Labels for significant events
    g.selectAll("text.label")
      .data(events.filter((e) => e.severity > 0.7))
      .join("text")
      .attr("class", "label")
      .attr("x", (d) => xScale(new Date(d.occurred_at)))
      .attr("y", h / 2 - 20)
      .attr("text-anchor", "middle")
      .attr("fill", "#94a3b8")
      .style("font-size", "9px")
      .text((d) => d.name.slice(0, 20));
  }, [events, width, height, onEventClick]);

  return <svg ref={svgRef} width={width} height={height} className="bg-background rounded-lg" />;
}
