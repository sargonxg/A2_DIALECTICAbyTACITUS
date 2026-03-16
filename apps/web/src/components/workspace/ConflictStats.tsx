"use client";

import type { Workspace } from "@/types/api";
import { glaslLevel, GLASL_COLORS } from "@/lib/utils";
import { Network, Users, Calendar, AlertTriangle } from "lucide-react";

export default function ConflictStats({ workspace }: { workspace: Workspace }) {
  const level = workspace.glasl_stage ? glaslLevel(workspace.glasl_stage) : null;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="card">
        <div className="flex items-center gap-2 text-text-secondary text-xs mb-1">
          <AlertTriangle size={14} /> Glasl Stage
        </div>
        <p className="text-2xl font-mono font-bold" style={{ color: level ? GLASL_COLORS[level] : undefined }}>
          {workspace.glasl_stage ?? "N/A"}
        </p>
        <p className="text-xs text-text-secondary">{level ?? "Not assessed"}</p>
      </div>
      <div className="card">
        <div className="flex items-center gap-2 text-text-secondary text-xs mb-1">
          <Network size={14} /> Graph
        </div>
        <p className="text-2xl font-mono font-bold text-text-primary">{workspace.node_count}</p>
        <p className="text-xs text-text-secondary">{workspace.edge_count} edges</p>
      </div>
      <div className="card">
        <div className="flex items-center gap-2 text-text-secondary text-xs mb-1">
          <Users size={14} /> Status
        </div>
        <p className="text-lg font-medium text-text-primary capitalize">{workspace.status ?? "Active"}</p>
        <p className="text-xs text-text-secondary">{workspace.kriesberg_phase ?? "N/A"}</p>
      </div>
      <div className="card">
        <div className="flex items-center gap-2 text-text-secondary text-xs mb-1">
          <Calendar size={14} /> Domain
        </div>
        <p className="text-lg font-medium text-accent capitalize">{workspace.domain}</p>
        <p className="text-xs text-text-secondary">{workspace.scale} scale</p>
      </div>
    </div>
  );
}
