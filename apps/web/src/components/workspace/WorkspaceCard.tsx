"use client";

import Link from "next/link";
import type { Workspace } from "@/types/api";
import { formatRelative, glaslLevel } from "@/lib/utils";
import { Network, Clock, Layers } from "lucide-react";

export default function WorkspaceCard({ workspace }: { workspace: Workspace }) {
  const level = workspace.glasl_stage ? glaslLevel(workspace.glasl_stage) : null;
  return (
    <Link href={`/workspaces/${workspace.id}`}>
      <div className="card-hover space-y-3">
        <div className="flex items-start justify-between">
          <h3 className="font-semibold text-text-primary truncate">{workspace.name}</h3>
          {level && (
            <span
              className="badge"
              style={{
                backgroundColor: level === "win-win" ? "#10b98120" : level === "win-lose" ? "#f59e0b20" : "#f43f5e20",
                color: level === "win-win" ? "#10b981" : level === "win-lose" ? "#f59e0b" : "#f43f5e",
              }}
            >
              Stage {workspace.glasl_stage}
            </span>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="badge bg-accent/10 text-accent">{workspace.domain}</span>
          <span className="badge bg-surface-hover text-text-secondary">{workspace.scale}</span>
          <span className="badge bg-surface-hover text-text-secondary">{workspace.tier}</span>
        </div>

        <div className="flex items-center justify-between text-xs text-text-secondary">
          <span className="flex items-center gap-1">
            <Network size={12} />
            {workspace.node_count} nodes &middot; {workspace.edge_count} edges
          </span>
          <span className="flex items-center gap-1">
            <Clock size={12} />
            {formatRelative(workspace.updated_at)}
          </span>
        </div>
      </div>
    </Link>
  );
}
