"use client";

import { useEffect, useState } from "react";
import { DataImportExport } from "@/components/admin/DataImportExport";
import { workspacesApi, type Workspace } from "@/lib/api";
import { Database, Clock, Loader2 } from "lucide-react";

export default function DataPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    workspacesApi.list()
      .then((res) => setWorkspaces(res.workspaces ?? []))
      .catch(() => setWorkspaces([]))
      .finally(() => setLoading(false));
  }, []);

  function formatDate(iso: string) {
    try {
      return new Date(iso).toLocaleString("en-GB", {
        day: "2-digit", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      });
    } catch { return iso; }
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Data Management</h1>
        <p className="text-[#a1a1aa] text-sm">Import, export, and seed graph data across workspaces.</p>
      </div>

      {/* Last ingest times */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Clock size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">Last Updated Per Workspace</h2>
        </div>
        {loading ? (
          <div className="flex items-center gap-2 text-[#71717a] text-sm">
            <Loader2 size={13} className="animate-spin" /> Loading…
          </div>
        ) : !workspaces.length ? (
          <p className="text-[#52525b] text-sm">No workspaces found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#27272a]">
                  <th className="text-left text-[#71717a] text-xs font-medium pb-2 pr-6">Workspace</th>
                  <th className="text-left text-[#71717a] text-xs font-medium pb-2 pr-6">Domain</th>
                  <th className="text-right text-[#71717a] text-xs font-medium pb-2 pr-6">Nodes</th>
                  <th className="text-right text-[#71717a] text-xs font-medium pb-2 pr-6">Edges</th>
                  <th className="text-left text-[#71717a] text-xs font-medium pb-2">Last Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272a]/50">
                {workspaces.map((ws) => (
                  <tr key={ws.id} className="hover:bg-[#27272a]/10 transition-colors">
                    <td className="py-2.5 pr-6">
                      <p className="text-[#fafafa] text-sm font-medium truncate max-w-[180px]">{ws.name}</p>
                      <p className="text-[#52525b] text-xs font-mono">{ws.id}</p>
                    </td>
                    <td className="py-2.5 pr-6 text-[#a1a1aa] text-xs capitalize">{ws.domain}</td>
                    <td className="py-2.5 pr-6 text-right text-[#a1a1aa] font-mono text-xs">{ws.node_count ?? "—"}</td>
                    <td className="py-2.5 pr-6 text-right text-[#a1a1aa] font-mono text-xs">{ws.edge_count ?? "—"}</td>
                    <td className="py-2.5 text-[#71717a] text-xs">{formatDate(ws.updated_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Import/Export component */}
      <DataImportExport />
    </div>
  );
}
