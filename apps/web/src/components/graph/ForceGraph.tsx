'use client';

import React, { useRef, useEffect, useCallback } from 'react';
import * as d3 from 'd3';
import type { GraphNode, GraphEdge } from '@/lib/api';

const NODE_COLORS: Record<string, string> = {
  actor:         '#3b82f6',
  conflict:      '#6366f1',
  event:         '#eab308',
  issue:         '#f97316',
  interest:      '#22c55e',
  process:       '#06b6d4',
  narrative:     '#ec4899',
  trust_state:   '#8b5cf6',
  power_dynamic: '#a855f7',
};

function nodeColor(label: string): string {
  return NODE_COLORS[label.toLowerCase()] ?? '#71717a';
}

function truncate(str: string, max = 16): string {
  return str.length > max ? str.slice(0, max - 1) + '\u2026' : str;
}

interface SimNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  name: string;
}

interface SimLink extends d3.SimulationLinkDatum<SimNode> {
  id: string;
  type: string;
  weight?: number;
}

interface ForceGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: GraphNode) => void;
  width?: number;
  height?: number;
}

export function ForceGraph({
  nodes,
  edges,
  onNodeClick,
  width = 800,
  height = 600,
}: ForceGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simRef = useRef<d3.Simulation<SimNode, SimLink> | null>(null);

  const handleNodeClick = useCallback(
    (node: GraphNode) => {
      if (onNodeClick) onNodeClick(node);
    },
    [onNodeClick],
  );

  useEffect(() => {
    const svgEl = svgRef.current;
    if (!svgEl) return;

    const svg = d3.select(svgEl);
    svg.selectAll('*').remove();

    if (nodes.length === 0) return;

    const simNodes: SimNode[] = nodes.map((n) => ({
      id: n.id,
      label: n.label,
      name: n.name,
    }));

    const nodeById = new Map(simNodes.map((n) => [n.id, n]));

    const simLinks: SimLink[] = edges
      .filter((e) => nodeById.has(e.source_id) && nodeById.has(e.target_id))
      .map((e) => ({
        id: e.id,
        source: e.source_id,
        target: e.target_id,
        type: e.type,
        weight: e.weight,
      }));

    const root = svg.append('g').attr('class', 'root');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on('zoom', (event) => {
        root.attr('transform', event.transform);
      });

    svg.call(zoom).on('dblclick.zoom', null);

    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 18)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .append('path')
      .attr('d', 'M 0,-5 L 10,0 L 0,5')
      .attr('fill', '#52525b')
      .style('stroke', 'none');

    const link = root
      .append('g')
      .selectAll('line')
      .data(simLinks)
      .join('line')
      .attr('stroke', '#3f3f46')
      .attr('stroke-width', (d) => Math.max(1, (d.weight ?? 0.5) * 2))
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', 'url(#arrowhead)');

    const nodeGroup = root
      .append('g')
      .selectAll<SVGGElement, SimNode>('g')
      .data(simNodes)
      .join('g')
      .attr('cursor', 'pointer')
      .on('click', (_event, d) => {
        const original = nodes.find((n) => n.id === d.id);
        if (original) handleNodeClick(original);
      });

    nodeGroup
      .append('circle')
      .attr('r', 10)
      .attr('fill', (d) => nodeColor(d.label))
      .attr('fill-opacity', 0.85)
      .attr('stroke', (d) => nodeColor(d.label))
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.4);

    nodeGroup
      .append('text')
      .attr('dy', 22)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('fill', '#a1a1aa')
      .attr('pointer-events', 'none')
      .text((d) => truncate(d.name));

    const drag = d3
      .drag<SVGGElement, SimNode>()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });

    nodeGroup.call(drag);

    nodeGroup
      .on('mouseenter', function (_event, d) {
        d3.select(this)
          .select('circle')
          .attr('r', 13)
          .attr('stroke-width', 2.5)
          .attr('stroke-opacity', 0.9)
          .attr('fill-opacity', 1);

        link
          .attr('stroke-opacity', (l) => {
            const src = typeof l.source === 'object' ? (l.source as SimNode).id : l.source;
            const tgt = typeof l.target === 'object' ? (l.target as SimNode).id : l.target;
            return src === d.id || tgt === d.id ? 1 : 0.1;
          })
          .attr('stroke', (l) => {
            const src = typeof l.source === 'object' ? (l.source as SimNode).id : l.source;
            const tgt = typeof l.target === 'object' ? (l.target as SimNode).id : l.target;
            return src === d.id || tgt === d.id ? '#0d9488' : '#3f3f46';
          });
      })
      .on('mouseleave', function () {
        d3.select(this)
          .select('circle')
          .attr('r', 10)
          .attr('stroke-width', 1.5)
          .attr('stroke-opacity', 0.4)
          .attr('fill-opacity', 0.85);

        link.attr('stroke-opacity', 0.6).attr('stroke', '#3f3f46');
      });

    const simulation = d3
      .forceSimulation<SimNode>(simNodes)
      .force(
        'link',
        d3
          .forceLink<SimNode, SimLink>(simLinks)
          .id((d) => d.id)
          .distance(80)
          .strength(0.5),
      )
      .force('charge', d3.forceManyBody().strength(-250))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(22))
      .alphaDecay(0.02);

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as SimNode).x ?? 0)
        .attr('y1', (d) => (d.source as SimNode).y ?? 0)
        .attr('x2', (d) => (d.target as SimNode).x ?? 0)
        .attr('y2', (d) => (d.target as SimNode).y ?? 0);

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    simRef.current = simulation;

    const fitTimer = setTimeout(() => {
      const rootNode = root.node() as SVGGElement | null;
      if (!rootNode) return;
      const bounds = rootNode.getBBox();
      const { x, y, width: bw, height: bh } = bounds;
      if (bw === 0 || bh === 0) return;
      const scale = Math.min(0.9, 0.9 / Math.max(bw / width, bh / height));
      const tx = width / 2 - scale * (x + bw / 2);
      const ty = height / 2 - scale * (y + bh / 2);
      svg
        .transition()
        .duration(600)
        .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
    }, 1200);

    return () => {
      clearTimeout(fitTimer);
      simulation.stop();
      simRef.current = null;
    };
  }, [nodes, edges, width, height, handleNodeClick]);

  if (nodes.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-[#27272a] bg-[#18181b]"
        style={{ width, height }}
      >
        <div className="text-center">
          <div className="mx-auto mb-3 h-12 w-12 rounded-full border border-[#27272a] bg-[#09090b] flex items-center justify-center">
            <svg
              viewBox="0 0 24 24"
              className="h-5 w-5 text-zinc-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <circle cx="12" cy="12" r="4" />
              <circle cx="4" cy="6" r="2" />
              <circle cx="20" cy="6" r="2" />
              <circle cx="4" cy="18" r="2" />
              <circle cx="20" cy="18" r="2" />
              <line x1="6" y1="7" x2="10" y2="11" />
              <line x1="18" y1="7" x2="14" y2="11" />
              <line x1="6" y1="17" x2="10" y2="13" />
              <line x1="18" y1="17" x2="14" y2="13" />
            </svg>
          </div>
          <p className="text-sm font-medium text-zinc-500">No graph data</p>
          <p className="text-xs text-zinc-600 mt-1">
            Ingest documents to populate the knowledge graph
          </p>
        </div>
      </div>
    );
  }

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="rounded-xl border border-[#27272a] bg-[#09090b]"
      style={{ display: 'block' }}
    />
  );
}

export default ForceGraph;