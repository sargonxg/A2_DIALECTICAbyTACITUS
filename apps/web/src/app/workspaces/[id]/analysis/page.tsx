'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Activity,
  Target,
  ShieldCheck,
  Zap,
  Network,
  BookOpen,
  CheckSquare,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import {
  useEscalation,
  useRipeness,
  useTrust,
  usePower,
  useQuality,
} from '@/hooks/useReasoning';
import { GlaslStageIndicator } from '@/components/analysis/GlaslStageIndicator';
import { RipenessGauge } from '@/components/analysis/RipenessGauge';
import { TrustMatrix } from '@/components/analysis/TrustMatrix';
import { PowerMap } from '@/components/analysis/PowerMap';
import { TheoryAssessment } from '@/components/analysis/TheoryAssessment';

// ─── Types ─────────────────────────────────────────────────────────────────────

type TabId = 'escalation' | 'ripeness' | 'trust' | 'power' | 'network' | 'theory' | 'quality';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

const TABS: Tab[] = [
  { id: 'escalation', label: 'Escalation', icon: <Activity className="w-3.5 h-3.5" /> },
  { id: 'ripeness',   label: 'Ripeness',   icon: <Target    className="w-3.5 h-3.5" /> },
  { id: 'trust',      label: 'Trust',      icon: <ShieldCheck className="w-3.5 h-3.5" /> },
  { id: 'power',      label: 'Power',      icon: <Zap       className="w-3.5 h-3.5" /> },
  { id: 'network',    label: 'Network',    icon: <Network   className="w-3.5 h-3.5" /> },
  { id: 'theory',     label: 'Theory',     icon: <BookOpen  className="w-3.5 h-3.5" /> },
  { id: 'quality',    label: 'Quality',    icon: <CheckSquare className="w-3.5 h-3.5" /> },
];

// ─── Helpers ───────────────────────────────────────────────────────────────────

function LoadingPane() {
  return (
    <div className="flex items-center justify-center h-48">
      <Loader2 className="w-7 h-7 text-zinc-600 animate-spin" />
    </div>
  );
}

function ErrorPane({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-5 flex items-start gap-3">
      <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
      <p className="text-sm text-zinc-400">{message}</p>
    </div>
  );
}

// ─── Tab content panels ────────────────────────────────────────────────────────

function EscalationPanel({ workspaceId }: { workspaceId: string }) {
  const { data, loading, error } = useEscalation(workspaceId);
  if (loading) return <LoadingPane />;
  if (error)   return <ErrorPane message={error} />;
  if (!data)   return <ErrorPane message="No escalation data available." />;

  return (
    <div className="space-y-5">
      <GlaslStageIndicator
        stage={data.stage_number ?? 1}
        level={data.level}
        confidence={data.confidence}
        interventionType={data.intervention_type}
      />

      {data.signals.length > 0 && (
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5">
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-4">
            Escalation Signals ({data.signals.length})
          </p>
          <div className="space-y-2">
            {data.signals.map((sig, i) => {
              const severityColor =
                sig.severity >= 0.7 ? '#ef4444' : sig.severity >= 0.4 ? '#eab308' : '#22c55e';
              return (
                <div
                  key={i}
                  className="flex items-start gap-3 rounded-lg border border-[#27272a] bg-zinc-900/30 px-3 py-2.5"
                >
                  <div
                    className="mt-1.5 h-2 w-2 rounded-full shrink-0"
                    style={{ backgroundColor: severityColor }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-zinc-300 capitalize">
                        {sig.type.replace(/_/g, ' ')}
                      </span>
                      <span
                        className="ml-auto text-[10px] font-semibold tabular-nums"
                        style={{ color: severityColor }}
                      >
                        {Math.round(sig.severity * 100)}%
                      </span>
                    </div>
                    <p className="text-xs text-zinc-500 mt-0.5">{sig.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {data.evidence.length > 0 && (
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5">
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-3">
            Evidence
          </p>
          <ul className="space-y-1.5">
            {data.evidence.map((ev, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-400">
                <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-violet-500 shrink-0" />
                {ev}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function RipenessPanel({ workspaceId }: { workspaceId: string }) {
  const { data, loading, error } = useRipeness(workspaceId);
  if (loading) return <LoadingPane />;
  if (error)   return <ErrorPane message={error} />;
  if (!data)   return <ErrorPane message="No ripeness data available." />;
  return <RipenessGauge data={data} />;
}

function TrustPanel({ workspaceId }: { workspaceId: string }) {
  const { data, loading, error } = useTrust(workspaceId);
  if (loading) return <LoadingPane />;
  if (error)   return <ErrorPane message={error} />;
  if (!data)   return <ErrorPane message="No trust data available." />;
  return <TrustMatrix data={data} />;
}

function PowerPanel({ workspaceId }: { workspaceId: string }) {
  const { data, loading, error } = usePower(workspaceId);
  if (loading) return <LoadingPane />;
  if (error)   return <ErrorPane message={error} />;
  if (!data)   return <ErrorPane message="No power data available." />;
  return <PowerMap data={data} />;
}

function NetworkPanel({ workspaceId }: { workspaceId: string }) {
  // Network metrics are fetched via reasoningApi.getNetwork but no dedicated hook yet;
  // use a direct fetch pattern inside this component.
  const [loaded] = useState(false);

  if (!loaded) {
    return (
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-6 text-center">
        <Network className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
        <p className="text-sm text-zinc-500">
          Network community detection and broker analysis are available via the API.
        </p>
        <p className="text-xs text-zinc-600 mt-1">
          Endpoint: <code className="text-violet-400">/v1/workspaces/{workspaceId}/network</code>
        </p>
      </div>
    );
  }

  return null;
}

function TheoryPanel({ workspaceId }: { workspaceId: string }) {
  return <TheoryAssessment workspaceId={workspaceId} />;
}

function QualityPanel({ workspaceId }: { workspaceId: string }) {
  const { data, loading, error } = useQuality(workspaceId);
  if (loading) return <LoadingPane />;
  if (error)   return <ErrorPane message={error} />;
  if (!data)   return <ErrorPane message="No quality data available." />;

  const qualityColor =
    data.overall_quality >= 0.7 ? '#22c55e' : data.overall_quality >= 0.4 ? '#eab308' : '#ef4444';

  return (
    <div className="space-y-5">
      {/* Overall score */}
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
              Overall Graph Quality
            </p>
            <p className="text-xs text-zinc-600 mt-0.5">
              Assessed {new Date(data.assessed_at).toLocaleDateString()}
            </p>
          </div>
          <div
            className="rounded-lg border px-4 py-2 text-center"
            style={{ borderColor: `${qualityColor}40`, backgroundColor: `${qualityColor}10` }}
          >
            <p className="text-2xl font-bold" style={{ color: qualityColor }}>
              {Math.round(data.overall_quality * 100)}%
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Completeness', value: data.completeness.score, tier: data.completeness.tier },
            { label: 'Consistency', value: data.consistency.score, sub: `${data.consistency.edge_violations} violations` },
            { label: 'Coverage', value: data.coverage.score, sub: `${Math.round(data.coverage.avg_confidence * 100)}% avg confidence` },
          ].map(({ label, value, tier, sub }) => {
            const c = value >= 0.7 ? '#22c55e' : value >= 0.4 ? '#eab308' : '#ef4444';
            return (
              <div
                key={label}
                className="rounded-lg border border-[#27272a] bg-zinc-900/30 p-3 text-center"
              >
                <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium mb-1">
                  {label}
                </p>
                <p className="text-lg font-bold" style={{ color: c }}>
                  {Math.round(value * 100)}%
                </p>
                {(tier ?? sub) && (
                  <p className="text-[10px] text-zinc-600 mt-0.5">{tier ?? sub}</p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Recommendations */}
      {data.recommendations.length > 0 && (
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5">
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-3">
            Recommendations
          </p>
          <ul className="space-y-2">
            {data.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-zinc-300">
                <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-violet-500 shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Missing types */}
      {data.completeness.missing_node_types.length > 0 && (
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-widest text-amber-600 mb-3">
            Missing Node Types
          </p>
          <div className="flex flex-wrap gap-2">
            {data.completeness.missing_node_types.map((t) => (
              <span
                key={t}
                className="rounded border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-xs text-amber-400 capitalize"
              >
                {t}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Page ──────────────────────────────────────────────────────────────────────

export default function AnalysisPage() {
  const params = useParams();
  const id = params.id as string;
  const [activeTab, setActiveTab] = useState<TabId>('escalation');

  return (
    <div className="p-6 max-w-5xl space-y-6">
      {/* Tab bar */}
      <div className="flex items-center gap-1 overflow-x-auto pb-0.5">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                : 'text-zinc-500 hover:text-zinc-300 hover:bg-[#27272a] border border-transparent'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Panel */}
      <div>
        {activeTab === 'escalation' && <EscalationPanel workspaceId={id} />}
        {activeTab === 'ripeness'   && <RipenessPanel   workspaceId={id} />}
        {activeTab === 'trust'      && <TrustPanel      workspaceId={id} />}
        {activeTab === 'power'      && <PowerPanel      workspaceId={id} />}
        {activeTab === 'network'    && <NetworkPanel    workspaceId={id} />}
        {activeTab === 'theory'     && <TheoryPanel     workspaceId={id} />}
        {activeTab === 'quality'    && <QualityPanel    workspaceId={id} />}
      </div>
    </div>
  );
}
