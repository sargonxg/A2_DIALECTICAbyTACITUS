"use client";

import { useState, useEffect, useCallback } from "react";
import { workspacesApi } from "@/lib/api";
import type { Workspace } from "@/lib/api";

export function useWorkspaceList(): {
  workspaces: Workspace[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
} {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function fetchWorkspaces() {
      setLoading(true);
      setError(null);
      try {
        const result = await workspacesApi.list();
        if (!cancelled) {
          setWorkspaces(result.workspaces ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load workspaces");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchWorkspaces();

    return () => {
      cancelled = true;
    };
  }, [tick]);

  const refetch = useCallback(() => {
    setTick((t) => t + 1);
  }, []);

  return { workspaces, loading, error, refetch };
}

export function useWorkspace(id: string): {
  workspace: Workspace | null;
  loading: boolean;
  error: string | null;
} {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchWorkspace() {
      setLoading(true);
      setError(null);
      try {
        const result = await workspacesApi.get(id);
        if (!cancelled) {
          setWorkspace(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load workspace");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchWorkspace();

    return () => {
      cancelled = true;
    };
  }, [id]);

  return { workspace, loading, error };
}
