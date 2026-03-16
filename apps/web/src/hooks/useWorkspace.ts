"use client";

import { useState, useEffect, useCallback } from "react";
import { workspacesApi, type Workspace } from "@/lib/api";

// ─── useWorkspaceList ─────────────────────────────────────────────────────────

interface WorkspaceListState {
  workspaces: Workspace[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useWorkspaceList(): WorkspaceListState {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const refetch = useCallback(() => {
    setTick((t) => t + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await workspacesApi.list();
        if (!cancelled) {
          setWorkspaces(result.workspaces ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load workspaces",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [tick]);

  return { workspaces, loading, error, refetch };
}

// ─── useWorkspace ─────────────────────────────────────────────────────────────

interface WorkspaceState {
  workspace: Workspace | null;
  loading: boolean;
  error: string | null;
}

export function useWorkspace(id: string): WorkspaceState {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await workspacesApi.get(id);
        if (!cancelled) {
          setWorkspace(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load workspace",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [id]);

  return { workspace, loading, error };
}
