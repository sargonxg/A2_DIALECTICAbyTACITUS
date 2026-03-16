"use client";

import { useWorkspaces } from "@/hooks/useApi";
import { LayoutDashboard } from "lucide-react";

export default function AdminWorkspacesPage() {
  const { data, isLoading } = useWorkspaces();
  const workspaces = data?.items ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2"><LayoutDashboard size={20} /> All Workspaces</h2>
      <div className="card">
        <table className="w-full text-sm">
          <thead><tr className="text-text-secondary text-left"><th className="pb-2">Name</th><th className="pb-2">Domain</th><th className="pb-2">Tier</th><th className="pb-2">Nodes</th><th className="pb-2">Edges</th></tr></thead>
          <tbody>
            {workspaces.map((ws) => (
              <tr key={ws.id} className="border-t border-border">
                <td className="py-2 text-text-primary">{ws.name}</td>
                <td className="py-2 capitalize text-text-secondary">{ws.domain}</td>
                <td className="py-2"><span className="badge bg-accent/10 text-accent">{ws.tier}</span></td>
                <td className="py-2 font-mono text-text-secondary">{ws.node_count}</td>
                <td className="py-2 font-mono text-text-secondary">{ws.edge_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {isLoading && <p className="text-text-secondary text-sm py-4 text-center">Loading...</p>}
      </div>
    </div>
  );
}
