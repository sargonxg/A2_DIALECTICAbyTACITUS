"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useGraphData(workspaceId: string | undefined) {
  return useQuery({
    queryKey: ["graph", workspaceId],
    queryFn: () => api.getGraph(workspaceId!),
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
    queryFn: () => api.getSubgraph(workspaceId!, nodeId!, depth),
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
