"use client";

import { useWorkspaces } from "@/hooks/useApi";
import { GitCompare } from "lucide-react";

export default function ComparePage() {
  const { data } = useWorkspaces();
  const workspaces = data?.items ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
        <GitCompare size={24} /> Compare Workspaces
      </h1>
      <p className="text-text-secondary">Select 2-4 workspaces to compare their conflict structures side-by-side.</p>

      {workspaces.length < 2 ? (
        <div className="card text-center py-12">
          <p className="text-text-secondary">You need at least 2 workspaces to compare. Create more workspaces first.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {workspaces.map((ws) => (
            <div key={ws.id} className="card-hover cursor-pointer">
              <h3 className="font-semibold text-text-primary">{ws.name}</h3>
              <p className="text-xs text-text-secondary capitalize">{ws.domain} &middot; {ws.scale}</p>
              <p className="text-xs text-text-secondary">{ws.node_count} nodes</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
