'use client';

import { useParams } from 'next/navigation';
import { Calendar, Globe, Layers, Activity, Hash, RefreshCw, AlertCircle } from 'lucide-react';
import { useWorkspace } from '@/hooks/useWorkspace';
import { useEscalation } from '@/hooks/useReasoning';
import { ConflictStats } from '@/components/workspace/ConflictStats';
import { GlaslStageIndicator } from '@/components/analysis/GlaslStageIndicator';
import { KriesbergPhaseTracker } from '@/components/analysis/KriesbergPhaseTracker';

function formatDate(d: string): string {
  try {
    return new Date(d).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return d;
  }
}

function MetaRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-[#27272a] last:border-0">
      <span className="mt-0.5 text-zinc-500 shrink-0">{icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">{label}</p>
        <p className="text-sm text-zinc-200 mt-0.5">{value}</p>
      </div>
    </div>
  );
}

export default function WorkspaceOverviewPage() {
  const params = useParams();
  const id = params.id as string;

  const { workspace, loading: wsLoading, error: wsError } = useWorkspace(id);
  const { data: escalation, loading: escLoading, error: escError } = useEscalation(id);

  if (wsLoading) {
    return (
      <div className="p-6 space-y-4 animate-pulse">
        <div className="h-32 rounded-xl bg-[#18181b] border border-[#27272a]" />
        <div className="h-48 rounded-xl bg-[#18181b] border border-[#27272a]" />
        <div className="h-48 rounded-xl bg-[#18181b] border border-[#27272a]" />
      </div>
    );
  }

  if (wsError || !workspace) {
    return (
      <div className="p-6">
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-zinc-100">Failed to load workspace</p>
            <p className="text-sm text-zinc-400 mt-1">{wsError ?? 'Workspace not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      {/* Metadata card */}
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-4">
          Workspace Metadata
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8">
          <div>
            <MetaRow
              icon={<Hash className="w-3.5 h-3.5" />}
              label="Workspace ID"
              value={workspace.id}
            />
            <MetaRow
              icon={<Globe className="w-3.5 h-3.5" />}
              label="Domain"
              value={workspace.domain}
            />
            <MetaRow
              icon={<Layers className="w-3.5 h-3.5" />}
              label="Scale"
              value={workspace.scale}
            />
          </div>
          <div>
            <MetaRow
              icon={<Activity className="w-3.5 h-3.5" />}
              label="Status"
              value={workspace.status}
            />
            <MetaRow
              icon={<Calendar className="w-3.5 h-3.5" />}
              label="Created"
              value={formatDate(workspace.created_at)}
            />
            <MetaRow
              icon={<RefreshCw className="w-3.5 h-3.5" />}
              label="Last Updated"
              value={formatDate(workspace.updated_at)}
            />
          </div>
        </div>
      </div>

      {/* Conflict stats */}
      <ConflictStats workspaceId={id} />

      {/* Glasl stage indicator */}
      {escLoading ? (
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] h-40 animate-pulse" />
      ) : escError ? (
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-4">
          <p className="text-xs text-zinc-500">Escalation data unavailable: {escError}</p>
        </div>
      ) : escalation ? (
        <GlaslStageIndicator
          stage={escalation.stage_number ?? 1}
          level={escalation.level}
          confidence={escalation.confidence}
          interventionType={escalation.intervention_type}
        />
      ) : null}

      {/* Kriesberg phase tracker */}
      {workspace.kriesberg_phase ? (
        <KriesbergPhaseTracker phase={workspace.kriesberg_phase} />
      ) : escalation ? (
        <KriesbergPhaseTracker phase="latent" />
      ) : null}
    </div>
  );
}
