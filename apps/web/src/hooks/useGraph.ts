"use client";

import { useState, useEffect, useCallback } from "react";
import { graphApi } from "@/lib/api";
import type { GraphNode, GraphEdge } from "@/lib/api";

export function useGraphData(workspaceId: string): {
  nodes: GraphNode[];
  edges: GraphEdge[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
} {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!workspaceId) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchGraph() {
      setLoading(true);
      setError(null);
      try {
        const [nodesResult, edgesResult] = await Promise.all([
          graphApi.getNodes(workspaceId),
          graphApi.getEdges(workspaceId),
        ]);
        if (!cancelled) {
          setNodes(nodesResult.nodes ?? []);
          setEdges(edgesResult.edges ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load graph data");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchGraph();

    return () => {
      cancelled = true;
    };
  }, [workspaceId, tick]);

  const refetch = useCallback(() => {
    setTick((t) => t + 1);
  }, []);

  return { nodes, edges, loading, error, refetch };
}
