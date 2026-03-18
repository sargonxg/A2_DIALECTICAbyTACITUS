"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { AnalysisRequest } from "@/types/api";

export function useAnalysis() {
  return useMutation({
    mutationFn: (data: AnalysisRequest) => api.analyze(data),
  });
}

export function useTheoryFrameworks() {
  return useQuery({
    queryKey: ["theory-frameworks"],
    queryFn: () => api.listFrameworks(),
    staleTime: 300_000,
  });
}

export function useTheoryMatch(workspaceId: string | undefined) {
  return useMutation({
    mutationFn: () => api.matchTheory(workspaceId!),
  });
}
