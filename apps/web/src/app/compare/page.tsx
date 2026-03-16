'use client';

import { useState } from 'react';
import {
  GitCompare,
  ChevronDown,
  Loader2,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
} from 'lucide-react';
import { useWorkspaceList } from '@/hooks/useWorkspace';
import { useEscalation, useRipeness, usePower, useTrust } from '@/hooks/useReasoning';
import type { Workspace } from '@/lib/api';

// ─── Helpers ───────────────────────────────────────────────────────────────────

function glaslColor(stage?: number | null): string {
  if (stage == null) return '#71717a';
  if (stage <= 3) return '#22c55e';
  if (stage <= 6) return '#eab308';
  return '#ef4444';
}

function DiffIndicator({ diff }: { diff: number | null }) {
  if (diff === null) return <Minus className="w-4 h-4 text-zinc-600" />;
  if (Math.abs(diff) < 0.01) return <Minus className="w-4 h-4 text-zinc-500" />;
  return diff > 0 ? (
    <TrendingUp className="w-4 h-4 text-green-500" />
  ) : (
    <TrendingDown className="w-4 h-4 text-red-500" />
  );
}

function pct(v: number | null | undefined): string {
  if (v == null) return '—';
  return `${Math.round(v * 100)}%`;
}

// ─── Single workspace selector ────────────────────────────────────────────────

function WorkspaceSelector({
  value,
  onChange,
  workspaces,
  loading,
  label,
  exclude,
}: {
  value: string;
  onChange: (id: string) => void;
  workspaces: Workspace[];
  loading: boolean;
  label: string;
  exclude?: string;
}) {
  return (
    <div className="flex-1 space-y-1.5">
      <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">{label}</p>
      <div className="relative">
        {loading ? (
          <div className="flex items-center gap-2 rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2.5">
            <Loader2 className="w-4 h-4 text-zinc-600 animate-spin" />
            <span className="text-sm text-zinc-600">Loading…</span>
          </div>
        ) : (
          <>
            <select
              value={value}
              onChange={(e) => onChange(e.target.value)}
              className="w-full appearance-none rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2.5 pr-8 text-sm text-zinc-100 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
            >
              <option value="">Select workspace…</option>
              {workspaces
                .filter((w) => w.id !== exclude)
                .map((w) => (
                  <option key={w.id} value={w.id} className="bg-[#18181b]">
                    {w.name}
                  </option>
                ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          </>
        )}
      </div>
    </div>
  );
}

// ─── Metric data fetcher + row ────────────────────────────────────────────────

function CompareContent({ idA, idB }: { idA: string; idB: string }) {
  const { data: escA, loading: escAL } = useEscalation(idA);
  const { data: escB, loading: escBL } = useEscalation(idB);
  const { data: ripA, loading: ripAL } = useRipeness(idA);
  const { data: ripB, loading: ripBL } = useRipeness(idB);
  const { data: powA, loading: powAL } = usePower(idA);
  const { data: powB, loading: powBL } = usePower(idB);
  const { data: truA, loading: truAL } = useTrust(idA);
  const { data: truB, loading: truBL } = useTrust(idB);

  type Row = {
    label: string;
    aVal: number | null;
    bVal: number | null;
    aDisplay: string;
    bDisplay: string;
    aColor: string;
    bColor: string;
    loading: boolean;
    higherIsBetter: boolean;
  };

  const rows: Row[] = [
    {
      label: 'Glasl Stage',
      aVal: escA?.stage_number != null ? escA.stage_number / 9 : null,
      bVal: escB?.stage_number != null ? escB.stage_number / 9 : null,
      aDisplay: escA?.stage_number != null ? `Stage ${escA.stage_number}` : '—',
      bDisplay: escB?.stage_number != null ? `Stage ${escB.stage_number}` : '—',
      aColor: glaslColor(escA?.stage_number),
      bColor: glaslColor(escB?.stage_number),
      loading: escAL || escBL,
      higherIsBetter: false,
    },
    {
      label: 'Escalation Confidence',
      aVal: escA?.confidence ?? null,
      bVal: escB?.confidence ?? null,
      aDisplay: pct(escA?.confidence),
      bDisplay: pct(escB?.confidence),
      aColor: '#a1a1aa',
      bColor: '#a1a1aa',
      loading: escAL || escBL,
      higherIsBetter: false,
    },
    {
      label: 'Ripeness Score',
      aVal: ripA?.overall_score ?? null,
      bVal: ripB?.overall_score ?? null,
      aDisplay: pct(ripA?.overall_score),
      bDisplay: pct(ripB?.overall_score),
      aColor: ripA?.is_ripe ? '#22c55e' : '#71717a',
      bColor: ripB?.is_ripe ? '#22c55e' : '#71717a',
      loading: ripAL || ripBL,
      higherIsBetter: true,
    },
    {
      label: 'MHS Score',
      aVal: ripA?.mhs_score ?? null,
      bVal: ripB?.mhs_score ?? null,
      aDisplay: pct(ripA?.mhs_score),
      bDisplay: pct(ripB?.mhs_score),
      aColor: '#0d9488',
      bColor: '#0d9488',
      loading: ripAL || ripBL,
      higherIsBetter: true,
    },
    {
      label: 'Power Asymmetry',
      aVal: powA?.average_asymmetry ?? null,
      bVal: powB?.average_asymmetry ?? null,
      aDisplay: pct(powA?.average_asymmetry),
      bDisplay: pct(powB?.average_asymmetry),
      aColor: powA?.average_asymmetry != null
        ? powA.average_asymmetry >= 0.7 ? '#ef4444' : powA.average_asymmetry >= 0.4 ? '#eab308' : '#22c55e'
        : '#71717a',
      bColor: powB?.average_asymmetry != null
        ? powB.average_asymmetry >= 0.7 ? '#ef4444' : powB.average_asymmetry >= 0.4 ? '#eab308' : '#22c55e'
        : '#71717a',
      loading: powAL || powBL,
      higherIsBetter: false,
    },
    {
      label: 'Average Trust',
      aVal: truA?.average_trust ?? null,
      bVal: truB?.average_trust ?? null,
      aDisplay: pct(truA?.average_trust),
      bDisplay: pct(truB?.average_trust),
      aColor: truA?.average_trust != null
        ? truA.average_trust >= 0.7 ? '#22c55e' : truA.average_trust >= 0.4 ? '#eab308' : '#ef4444'
        : '#71717a',
      bColor: truB?.average_trust != null
        ? truB.average_trust >= 0.7 ? '#22c55e' : truB.average_trust >= 0.4 ? '#eab308' : '#ef4444'
        : '#71717a',
      loading: truAL || truBL,
      higherIsBetter: true,
    },
  ];

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[#27272a]">
            <th className="text-left py-3 px-4 text-xs font-semibold uppercase tracking-widest text-zinc-500 w-40">
              Metric
            </th>
            <th className="text-center py-3 px-4 text-xs font-semibold uppercase tracking-widest text-violet-400">
              Workspace A
            </th>
            <th className="text-center py-3 px-4 text-xs font-semibold uppercase tracking-widest text-zinc-500">
              Diff
            </th>
            <th className="text-center py-3 px-4 text-xs font-semibold uppercase tracking-widest text-teal-400">
              Workspace B
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const diff =
              row.aVal != null && row.bVal != null ? row.aVal - row.bVal : null;

            // Which side is "better"?
            const aWins =
              diff !== null &&
              ((row.higherIsBetter && diff > 0.02) || (!row.higherIsBetter && diff < -0.02));
            const bWins =
              diff !== null &&
              ((row.higherIsBetter && diff < -0.02) || (!row.higherIsBetter && diff > 0.02));

            return (
              <tr key={row.label} className="border-b border-[#27272a]/50 hover:bg-zinc-800/20 transition-colors">
                <td className="py-3 px-4 text-zinc-500 text-xs font-medium">{row.label}</td>
                <td className="py-3 px-4 text-center">
                  {row.loading ? (
                    <Loader2 className="w-3.5 h-3.5 text-zinc-600 animate-spin mx-auto" />
                  ) : (
                    <span
                      className={`text-sm font-semibold tabular-nums ${aWins ? 'ring-1 ring-current rounded px-1.5 py-0.5' : ''}`}
                      style={{ color: row.aColor }}
                    >
                      {row.aDisplay}
                    </span>
                  )}
                </td>
                <td className="py-3 px-4 text-center">
                  {row.loading ? null : (
                    <div className="flex items-center justify-center gap-1">
                      <DiffIndicator diff={diff} />
                      {diff !== null && Math.abs(diff) > 0.005 && (
                        <span className="text-[10px] text-zinc-600 tabular-nums">
                          {Math.abs(Math.round(diff * 100))}%
                        </span>
                      )}
                    </div>
                  )}
                </td>
                <td className="py-3 px-4 text-center">
                  {row.loading ? (
                    <Loader2 className="w-3.5 h-3.5 text-zinc-600 animate-spin mx-auto" />
                  ) : (
                    <span
                      className={`text-sm font-semibold tabular-nums ${bWins ? 'ring-1 ring-current rounded px-1.5 py-0.5' : ''}`}
                      style={{ color: row.bColor }}
                    >
                      {row.bDisplay}
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ─── Page ──────────────────────────────────────────────────────────────────────

export default function ComparePage() {
  const { workspaces, loading: wsLoading } = useWorkspaceList();

  const [idA, setIdA] = useState('');
  const [idB, setIdB] = useState('');

  const wsA = workspaces.find((w) => w.id === idA);
  const wsB = workspaces.find((w) => w.id === idB);

  const canCompare = Boolean(idA && idB && idA !== idB);

  return (
    <div className="min-h-full p-6 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-violet-500/20 border border-violet-500/30">
          <GitCompare className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-zinc-100">Compare Workspaces</h1>
          <p className="text-sm text-zinc-500">
            Side-by-side analysis comparison of two conflict workspaces.
          </p>
        </div>
      </div>

      {/* Workspace selectors */}
      <div className="flex flex-col sm:flex-row gap-4">
        <WorkspaceSelector
          value={idA}
          onChange={setIdA}
          workspaces={workspaces}
          loading={wsLoading}
          label="Workspace A"
          exclude={idB}
        />
        <div className="flex items-end pb-2.5 shrink-0">
          <GitCompare className="w-5 h-5 text-zinc-700" />
        </div>
        <WorkspaceSelector
          value={idB}
          onChange={setIdB}
          workspaces={workspaces}
          loading={wsLoading}
          label="Workspace B"
          exclude={idA}
        />
      </div>

      {/* Workspace name headers */}
      {canCompare && wsA && wsB && (
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-lg border border-violet-500/30 bg-violet-500/10 px-4 py-2.5">
            <p className="text-[10px] uppercase tracking-widest text-violet-500 font-medium mb-0.5">
              Workspace A
            </p>
            <p className="text-sm font-semibold text-zinc-100 truncate">{wsA.name}</p>
            <p className="text-xs text-zinc-500">{wsA.domain} · {wsA.scale}</p>
          </div>
          <div className="rounded-lg border border-teal-500/30 bg-teal-500/10 px-4 py-2.5">
            <p className="text-[10px] uppercase tracking-widest text-teal-500 font-medium mb-0.5">
              Workspace B
            </p>
            <p className="text-sm font-semibold text-zinc-100 truncate">{wsB.name}</p>
            <p className="text-xs text-zinc-500">{wsB.domain} · {wsB.scale}</p>
          </div>
        </div>
      )}

      {/* Comparison table */}
      {canCompare ? (
        <CompareContent idA={idA} idB={idB} />
      ) : (
        <div className="rounded-xl border border-dashed border-[#27272a] p-12 text-center">
          <AlertCircle className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-600">
            Select two different workspaces to compare their analysis metrics.
          </p>
        </div>
      )}
    </div>
  );
}
