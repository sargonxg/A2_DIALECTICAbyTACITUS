"use client";

import type { Workspace } from "@/lib/api";
import { Calendar, Layers, GitBranch, Network } from "lucide-react";

interface WorkspaceCardProps {
  workspace: Workspace;
  onClick?: () => void;
}

function getGlaslColor(stage?: number): string {
  if (stage === undefined || stage === null) return "text-[#a1a1aa]";
  if (stage <= 3) return "text-green-500";
  if (stage <= 6) return "text-yellow-500";
  return "text-red-500";
}

function getGlaslBg(stage?: number): string {
  if (stage === undefined || stage === null) return "bg-[#27272a] text-[#a1a1aa]";
  if (stage <= 3) return "bg-green-500/10 text-green-500";
  if (stage <= 6) return "bg-yellow-500/10 text-yellow-500";
  return "bg-red-500/10 text-red-500";
}

function getGlaslLabel(stage?: number): string {
  if (stage === undefined || stage === null) return "Unknown";
  if (stage <= 3) return `Stage ${stage} — Win-Win`;
  if (stage <= 6) return `Stage ${stage} — Win-Lose`;
  return `Stage ${stage} — Lose-Lose`;
}

const DOMAIN_COLORS: Record<string, string> = {
  interpersonal: "bg-blue-500/10 text-blue-400",
  workplace: "bg-cyan-500/10 text-cyan-400",
  commercial: "bg-green-500/10 text-green-400",
  legal: "bg-orange-500/10 text-orange-400",
  political: "bg-indigo-500/10 text-indigo-400",
  armed: "bg-red-500/10 text-red-400",
};

const SCALE_COLORS: Record<string, string> = {
  micro: "bg-violet-500/10 text-violet-400",
  meso: "bg-purple-500/10 text-purple-400",
  macro: "bg-pink-500/10 text-pink-400",
  meta: "bg-rose-500/10 text-rose-400",
};

function formatDate(dateString: string): string {
  try {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateString;
  }
}

export function WorkspaceCard({ workspace, onClick }: WorkspaceCardProps) {
  const domainColor = DOMAIN_COLORS[workspace.domain] ?? "bg-[#27272a] text-[#a1a1aa]";
  const scaleColor = SCALE_COLORS[workspace.scale] ?? "bg-[#27272a] text-[#a1a1aa]";
  const glaslBg = getGlaslBg(workspace.glasl_stage);
  const glaslLabel = getGlaslLabel(workspace.glasl_stage);

  return (
    <div
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => { if (e.key === "Enter" || e.key === " ") onClick(); } : undefined}
      className={`
        bg-[#18181b] border border-[#27272a] rounded-lg p-4 transition-all
        ${onClick ? "cursor-pointer hover:border-teal-600 hover:bg-[#1c1c1f] focus:outline-none focus:border-teal-600" : ""}
      `}
    >
      {/* Header: name + badges */}
      <div className="mb-3">
        <h3 className="text-[#fafafa] font-semibold text-base truncate mb-2">
          {workspace.name}
        </h3>
        <div className="flex flex-wrap gap-1.5">
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${domainColor}`}>
            {workspace.domain}
          </span>
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${scaleColor}`}>
            {workspace.scale}
          </span>
        </div>
      </div>

      {/* Glasl stage */}
      <div className="mb-3">
        <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium ${glaslBg}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${getGlaslColor(workspace.glasl_stage).replace("text-", "bg-")}`} />
          {glaslLabel}
        </div>
      </div>

      {/* Kriesberg phase */}
      {workspace.kriesberg_phase && (
        <div className="mb-3 flex items-center gap-1.5">
          <GitBranch size={12} className="text-[#a1a1aa] flex-shrink-0" />
          <span className="text-[#a1a1aa] text-xs capitalize">
            {workspace.kriesberg_phase}
          </span>
        </div>
      )}

      {/* Node/edge counts */}
      <div className="flex items-center gap-4 mb-3">
        {workspace.node_count !== undefined && (
          <div className="flex items-center gap-1.5">
            <Layers size={12} className="text-[#a1a1aa]" />
            <span className="text-[#a1a1aa] text-xs">
              {workspace.node_count} node{workspace.node_count !== 1 ? "s" : ""}
            </span>
          </div>
        )}
        {workspace.edge_count !== undefined && (
          <div className="flex items-center gap-1.5">
            <Network size={12} className="text-[#a1a1aa]" />
            <span className="text-[#a1a1aa] text-xs">
              {workspace.edge_count} edge{workspace.edge_count !== 1 ? "s" : ""}
            </span>
          </div>
        )}
      </div>

      {/* Created date */}
      <div className="flex items-center gap-1.5 border-t border-[#27272a] pt-3">
        <Calendar size={12} className="text-[#52525b]" />
        <span className="text-[#52525b] text-xs">
          Created {formatDate(workspace.created_at)}
        </span>
      </div>
    </div>
  );
}
