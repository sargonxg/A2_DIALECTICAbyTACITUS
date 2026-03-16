"use client";

import { useParams } from "next/navigation";
import { useWorkspaceDetail } from "@/hooks/useApi";
import ConflictStats from "@/components/workspace/ConflictStats";
import GlaslStageIndicator from "@/components/analysis/GlaslStageIndicator";
import KriesbergPhaseTracker from "@/components/analysis/KriesbergPhaseTracker";
import Link from "next/link";
import { Brain, Upload, Network } from "lucide-react";

export default function WorkspaceOverview() {
  const { id } = useParams();
  const { data: workspace, isLoading } = useWorkspaceDetail(id as string);

  if (isLoading || !workspace) {
    return <div className="space-y-4">{[1, 2, 3].map((i) => <div key={i} className="card h-24 animate-pulse bg-surface-hover" />)}</div>;
  }

  return (
    <div className="space-y-6">
      <ConflictStats workspace={workspace} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {workspace.glasl_stage && <GlaslStageIndicator currentStage={workspace.glasl_stage} />}
        <KriesbergPhaseTracker currentPhase={workspace.kriesberg_phase} />
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href={`/workspaces/${id}/ingest`} className="card-hover flex items-center gap-3">
          <Upload size={20} className="text-accent" />
          <div>
            <p className="font-medium text-text-primary">Ingest Documents</p>
            <p className="text-xs text-text-secondary">Upload and extract entities</p>
          </div>
        </Link>
        <Link href={`/workspaces/${id}/graph`} className="card-hover flex items-center gap-3">
          <Network size={20} className="text-accent" />
          <div>
            <p className="font-medium text-text-primary">Explore Graph</p>
            <p className="text-xs text-text-secondary">Visualize conflict network</p>
          </div>
        </Link>
        <Link href={`/workspaces/${id}/analysis`} className="card-hover flex items-center gap-3">
          <Brain size={20} className="text-accent" />
          <div>
            <p className="font-medium text-text-primary">Analyze</p>
            <p className="text-xs text-text-secondary">AI-powered conflict analysis</p>
          </div>
        </Link>
      </div>

      {workspace.node_count === 0 && (
        <div className="card text-center py-12">
          <p className="text-text-secondary mb-4">This workspace is empty. Start by ingesting some documents.</p>
          <Link href={`/workspaces/${id}/ingest`} className="btn-primary">Ingest Documents</Link>
        </div>
      )}
    </div>
  );
}
