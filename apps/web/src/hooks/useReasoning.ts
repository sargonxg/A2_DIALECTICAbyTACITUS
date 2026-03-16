"use client";

import { useState, useEffect } from "react";
import { reasoningApi } from "@/lib/api";
import type {
  EscalationAssessment,
  RipenessAssessment,
  PowerMap,
  TrustMatrix,
  QualityDashboard,
} from "@/lib/api";

export function useEscalation(workspaceId: string): {
  data: EscalationAssessment | null;
  loading: boolean;
  error: string | null;
} {
  const [data, setData] = useState<EscalationAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetch() {
      setLoading(true);
      setError(null);
      try {
        const result = await reasoningApi.getEscalation(workspaceId);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load escalation data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetch();
    return () => { cancelled = true; };
  }, [workspaceId]);

  return { data, loading, error };
}

export function useRipeness(workspaceId: string): {
  data: RipenessAssessment | null;
  loading: boolean;
  error: string | null;
} {
  const [data, setData] = useState<RipenessAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetch() {
      setLoading(true);
      setError(null);
      try {
        const result = await reasoningApi.getRipeness(workspaceId);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load ripeness data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetch();
    return () => { cancelled = true; };
  }, [workspaceId]);

  return { data, loading, error };
}

export function usePower(workspaceId: string): {
  data: PowerMap | null;
  loading: boolean;
  error: string | null;
} {
  const [data, setData] = useState<PowerMap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetch() {
      setLoading(true);
      setError(null);
      try {
        const result = await reasoningApi.getPower(workspaceId);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load power data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetch();
    return () => { cancelled = true; };
  }, [workspaceId]);

  return { data, loading, error };
}

export function useTrust(workspaceId: string): {
  data: TrustMatrix | null;
  loading: boolean;
  error: string | null;
} {
  const [data, setData] = useState<TrustMatrix | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetch() {
      setLoading(true);
      setError(null);
      try {
        const result = await reasoningApi.getTrust(workspaceId);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load trust data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetch();
    return () => { cancelled = true; };
  }, [workspaceId]);

  return { data, loading, error };
}

export function useQuality(workspaceId: string): {
  data: QualityDashboard | null;
  loading: boolean;
  error: string | null;
} {
  const [data, setData] = useState<QualityDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetch() {
      setLoading(true);
      setError(null);
      try {
        const result = await reasoningApi.getQuality(workspaceId);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load quality data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetch();
    return () => { cancelled = true; };
  }, [workspaceId]);

  return { data, loading, error };
}
