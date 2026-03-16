"use client";

import { useEffect, useState, useCallback } from "react";
import { workspacesApi, type Workspace } from "@/lib/api";
import {
  FolderOpen,
  Trash2,
  RefreshCw,
  Loader2,
  Plus,
  Database,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";

const SAMPLE_WORKSPACES = [
  { name: "JCPOA Nuclear Negotiations", domain: "diplomatic", scale: "international" },
  { name: "HR Workplace Mediation", domain: "organizational", scale: "interpersonal" },
  { name: "Commercial Contract Dispute", domain: "commercial", scale: "organizational" },
];

type SeedStatus = "idle" | "loading" | "done" | "error";

export default function AdminWorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [seedStatus, setSeedStatus] = useState<SeedStatus>("idle");

  const fetchWorkspaces = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await workspacesApi.list();
      setWorkspaces(res.workspaces ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspaces");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  async function handleDelete(id: string) {
    if (!confirm("Delete this workspace and all its data? This cannot be undone.")) return;
    setDeletingId(id);
    try {
      await workspacesApi.delete(id);
      setWorkspaces((ws) => ws.filter((w) => w.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setDeletingId(null);
    }
  }

  async function handleSeedAll() {
    setSeedStatus("loading");
    try {
      for (const ws of SAMPLE_WORKSPACES) {
        await workspacesApi.create(ws);
      }
      setSeedStatus("done");
      fetchWorkspaces();
      setTimeout(() => setSeedStatus("idle"), 3000);
    } catch {
      setSeedStatus("error");
      setTimeout(() => setSeedStatus("idle"), 3000);
    }
  }

  function formatDate(iso: string) {
    try {
      return new Date(iso).toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric",
      });
    } catch {
      return iso;
    }
  }

  return (
    <div className="p-8 max-w-6xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Workspaces</h1>
          <p className="text-[#a1a1aa] text-sm">All conflict workspaces in the system.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSeedAll}
            disabled={seedStatus === "loading"}
            className="flex items-center gap-1.5 px-3 py-2 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#a1a1aa] hover:text-[#fafafa] text-sm transition-colors disabled:opacity-50"
          >
            {seedStatus === "loading" ? (
              <Loader2 size={14} className="animate-spin" />
            ) : seedStatus === "done" ? (
              <CheckCircle2 size={14} className="text-green-400" />
            ) : (
              <Database size={14} />
            )}
            {seedStatus === "done" ? "Seeded!" : "Load Sample Data"}
          </button>
          <button
            onClick={fetchWorkspaces}
            disabled={loading}
            className="p-2 rounded-md text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors disabled:opacity-50"
            aria-label="Refresh"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg mb-6 text-red-400 text-sm">
          <AlertTriangle size={14} />
          {error}
        </div>
      )}

      {loading && !workspaces.length ? (
        <div className="flex items-center gap-2 text-[#71717a] text-sm">
          <Loader2 size={14} className="animate-spin" /> Loading workspaces…
        </div>
      ) : !workspaces.length ? (
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-12 text-center">
          <FolderOpen size={32} className="text-[#3f3f46] mx-auto mb-3" />
          <p className="text-[#71717a] text-sm mb-4">No workspaces found.</p>
          <button
            onClick={handleSeedAll}
            disabled={seedStatus === "loading"}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-teal-600/20 hover:bg-teal-600/30 border border-teal-600/30 text-teal-400 text-sm transition-colors"
          >
            <Plus size={14} /> Load Sample Workspaces
          </button>
        </div>
      ) : (
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#27272a] bg-[#09090b]/40">
                  <th className="text-left text-[#71717a] text-xs font-medium px-4 py-3">Name</th>
                  <th className="text-left text-[#71717a] text-xs font-medium px-4 py-3">Domain</th>
                  <th className="text-left text-[#71717a] text-xs font-medium px-4 py-3">Scale</th>
                  <th className="text-right text-[#71717a] text-xs font-medium px-4 py-3">Nodes</th>
                  <th className="text-right text-[#71717a] text-xs font-medium px-4 py-3">Edges</th>
                  <th className="text-left text-[#71717a] text-xs font-medium px-4 py-3">Created</th>
                  <th className="text-left text-[#71717a] text-xs font-medium px-4 py-3">ID</th>
                  <th className="px-4 py-3 w-10" />
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272a]/60">
                {workspaces.map((ws) => (
                  <tr key={ws.id} className="hover:bg-[#27272a]/20 transition-colors">
                    <td className="px-4 py-3">
                      <p className="text-[#fafafa] font-medium truncate max-w-[200px]">{ws.name}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-[#a1a1aa] text-xs capitalize">{ws.domain}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-[#a1a1aa] text-xs capitalize">{ws.scale}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-[#a1a1aa] font-mono text-xs">{ws.node_count ?? "—"}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-[#a1a1aa] font-mono text-xs">{ws.edge_count ?? "—"}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-[#71717a] text-xs">{formatDate(ws.created_at)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <code className="text-[#52525b] text-xs font-mono">{ws.id}</code>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDelete(ws.id)}
                        disabled={deletingId === ws.id}
                        className="p-1.5 rounded-md text-[#52525b] hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                        title="Delete workspace"
                        aria-label="Delete workspace"
                      >
                        {deletingId === ws.id ? (
                          <Loader2 size={13} className="animate-spin" />
                        ) : (
                          <Trash2 size={13} />
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-2 border-t border-[#27272a] text-[#52525b] text-xs">
            {workspaces.length} workspace{workspaces.length !== 1 ? "s" : ""}
          </div>
        </div>
      )}
    </div>
  );
}
