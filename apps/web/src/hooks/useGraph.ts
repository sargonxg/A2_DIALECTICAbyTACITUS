"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { WorkspaceGraphResponse } from "@/types/api";
import type { GraphData, GraphNode, GraphLink } from "@/types/graph";

/** Adapt WorkspaceGraphResponse to the GraphData shape expected by ForceGraph */
function toGraphData(resp: WorkspaceGraphResponse): GraphData {
  const nodes: GraphNode[] = resp.nodes.map((n) => ({
    id: n.id,
    label: n.label,
    node_type: (n.type as GraphNode["node_type"]) ?? "actor",
    name: n.label,
    confidence: typeof n.properties?.confidence === "number" ? n.properties.confidence : 1,
    properties: n.properties,
    x: n.x,
    y: n.y,
    fx: n.fx,
    fy: n.fy,
    vx: n.vx,
    vy: n.vy,
  }));
  const links: GraphLink[] = resp.edges.map((e) => ({
    id: e.id ?? `${e.source}-${e.type}-${e.target}`,
    source: e.source,
    target: e.target,
    edge_type: e.type,
    weight: e.weight ?? 1,
    confidence: 1,
  }));
  return { nodes, links };
}

export function useGraphData(workspaceId: string | undefined) {
  return useQuery({
    queryKey: ["graph", workspaceId],
    queryFn: () => api.getGraph(workspaceId!).then(toGraphData),
    enabled: !!workspaceId,
    staleTime: 30_000,
  });
}

export function useSubgraph(
  workspaceId: string | undefined,
  nodeId: string | undefined,
  depth = 2,
) {
  return useQuery({
    queryKey: ["subgraph", workspaceId, nodeId, depth],
    queryFn: () => api.getSubgraph(workspaceId!, nodeId!, depth).then(toGraphData),
    enabled: !!workspaceId && !!nodeId,
    staleTime: 30_000,
  });
}

export function useEntities(
  workspaceId: string | undefined,
  nodeType?: string,
) {
  return useQuery({
    queryKey: ["entities", workspaceId, nodeType],
    queryFn: () => api.getEntities(workspaceId!, nodeType),
    enabled: !!workspaceId,
    staleTime: 30_000,
  });
}
