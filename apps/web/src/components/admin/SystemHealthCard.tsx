"use client";

import { useEffect, useState, useCallback } from "react";
import { RefreshCw, CheckCircle2, XCircle, Loader2, Wifi } from "lucide-react";
import { healthApi } from "@/lib/api";

interface HealthData {
  status: string;
  version: string;
  graph_backend: string;
}

export function SystemHealthCard() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    const start = performance.now();
    try {
      const data = await healthApi.get();
      const elapsed = Math.round(performance.now() - start);
      setHealth(data);
      setLatencyMs(elapsed);
      setLastChecked(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reach API");
      setHealth(null);
      setLatencyMs(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  const apiOnline = !!health && health.status === "ok";

  return (
    <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Wifi size={16} className="text-[#71717a]" />
          <h3 className="text-[#fafafa] text-sm font-semibold">API Health</h3>
        </div>
        <button
          onClick={fetchHealth}
          disabled={loading}
          className="p-1.5 rounded-md text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors disabled:opacity-50"
          title="Refresh"
          aria-label="Refresh health status"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {loading && !health && (
        <div className="flex items-center gap-2 text-[#71717a] text-sm">
          <Loader2 size={14} className="animate-spin" />
          Checking API status…
        </div>
      )}

      {!loading && error && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <XCircle size={16} className="text-red-400" />
            <span className="text-red-400 text-sm font-medium">API Unreachable</span>
          </div>
          <p className="text-[#71717a] text-xs font-mono bg-[#09090b] rounded px-3 py-2 border border-[#27272a]">
            {error}
          </p>
        </div>
      )}

      {health && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <p className="text-[#71717a] text-xs mb-1">Status</p>
            <div className="flex items-center gap-1.5">
              {apiOnline ? (
                <CheckCircle2 size={14} className="text-green-400" />
              ) : (
                <XCircle size={14} className="text-red-400" />
              )}
              <span
                className={`text-sm font-medium ${
                  apiOnline ? "text-green-400" : "text-red-400"
                }`}
              >
                {apiOnline ? "Online" : health.status}
              </span>
            </div>
          </div>

          <div>
            <p className="text-[#71717a] text-xs mb-1">Version</p>
            <p className="text-[#fafafa] text-sm font-mono">{health.version || "—"}</p>
          </div>

          <div>
            <p className="text-[#71717a] text-xs mb-1">Graph Backend</p>
            <p className="text-[#fafafa] text-sm font-mono">
              {health.graph_backend || "—"}
            </p>
          </div>

          <div>
            <p className="text-[#71717a] text-xs mb-1">Latency</p>
            <p
              className={`text-sm font-mono ${
                latencyMs !== null && latencyMs < 200
                  ? "text-green-400"
                  : latencyMs !== null && latencyMs < 500
                  ? "text-yellow-400"
                  : "text-red-400"
              }`}
            >
              {latencyMs !== null ? `${latencyMs}ms` : "—"}
            </p>
          </div>
        </div>
      )}

      {lastChecked && (
        <p className="text-[#52525b] text-xs mt-4">
          Last checked: {lastChecked.toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
