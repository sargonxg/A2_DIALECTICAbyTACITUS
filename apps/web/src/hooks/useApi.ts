"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useWorkspaces(page = 1) {
  return useQuery({
    queryKey: ["workspaces", page],
    queryFn: () => api.listWorkspaces(page),
    staleTime: 15_000,
  });
}

export function useWorkspaceDetail(id: string | undefined) {
  return useQuery({
    queryKey: ["workspace", id],
    queryFn: () => api.getWorkspace(id!),
    enabled: !!id,
    staleTime: 15_000,
  });
}

export function useApiKeys() {
  return useQuery({
    queryKey: ["api-keys"],
    queryFn: () => api.listApiKeys(),
    staleTime: 30_000,
  });
}

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => api.health(),
    staleTime: 60_000,
  });
}
