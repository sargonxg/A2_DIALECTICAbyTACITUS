'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {
  Users,
  CalendarDays,
  AlertTriangle,
  GitFork,
  ShieldCheck,
  RefreshCw,
  BarChart3,
  Layers,
} from 'lucide-react';
import { graphApi, reasoningApi, type Workspace, type QualityDashboard } from '@/lib/api';

interface ConflictStatsProps {
  workspaceId: string;
  workspace: Workspace;
}

interface StatItem {
  label: string;
  count: number | null;
  icon: React.ReactNode;
  color: string;
  nodeType: string;
}

function qualityColor(score: number): string {
  if (score >= 0.75) return '#22c55e';
  if (score >= 0.5) return '#eab308';
  return '#ef4444';
}

function tierBadgeClass(tier: string): string {
  const t = tier.toLowerCase();
  if (t === 'comprehensive' || t === 'high' || t === 'complete') {
    return 'bg-green-600/20 text-green-400 border-green-600/30';
  }
  if (t === 'adequate' || t === 'medium' || t === 'partial') {
    return 'bg-yellow-600/20 text-yellow-400 border-yellow-600/30';
  }
  if (t === 'minimal' || t === 'low' || t === 'sparse') {
    return 'bg-red-600/20 text-red-400 border-red-600/30';
  }
  return 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30';
}

interface StatCardProps {
  item: StatItem;
  loading: boolean;
}

function StatCard({ item, loading }: StatCardProps) {
  return (
    <div className="rounded-lg border border-[#27272a] bg-zinc-900/40 p-4 space-y-2 hover:border-zinc-600/50 transition-colors">
      <div className="flex items-center justify-between">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${item.color}18`, color: item.color }}
        >
          {item.icon}
        </div>
        {loading ? (
          <div className="w-10 h-6 bg-zinc-800 rounded animate-pulse" />
        ) : (
          <span className="text-2xl font-bold text-zinc-100 tabular-nums">
            {item.count ?? '—'}
          </span>
        )}
      </div>
      <p className="text-xs text-zinc-400 font-medium">{item.label}</p>
    </div>
  );
}

export function ConflictStats({ workspaceId, workspace }: ConflictStatsProps) {
  const [counts, setCounts] = useState<Record<string, number | null>>({
    Actor: null,
    Event: null,
    Issue: null,
    Process: null,
  });
  const [quality, setQuality] = useState<QualityDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [actorRes, eventRes, issueRes, processRes, qualityRes] = await Promise.allSettled([
        graphApi.getNodes(workspaceId, 'Actor'),
        graphApi.getNodes(workspaceId, 'Event'),
        graphApi.getNodes(workspaceId, 'Issue'),
        graphApi.getNodes(workspaceId, 'Process'),
        reasoningApi.getQuality(workspaceId),
      ]);

      setCounts({
        Actor: actorRes.status === 'fulfilled' ? actorRes.value.nodes.length : null,
        Event: eventRes.status === 'fulfilled' ? eventRes.value.nodes.length : null,
        Issue: issueRes.status === 'fulfilled' ? issueRes.value.nodes.length : null,
        Process: processRes.status === 'fulfilled' ? processRes.value.nodes.length : null,
      });

      if (qualityRes.status === 'fulfilled') {
        setQuality(qualityRes.value);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  const statItems: StatItem[] = [
    {
      label: 'Actors',
      count: counts.Actor,
      icon: <Users className="w-4 h-4" />,
      color: '#0d9488',
      nodeType: 'Actor',
    },
    {
      label: 'Events',
      count: counts.Event,
      icon: <CalendarDays className="w-4 h-4" />,
      color: '#6366f1',
      nodeType: 'Event',
    },
    {
      label: 'Issues',
      count: counts.Issue,
      icon: <AlertTriangle className="w-4 h-4" />,
      color: '#f59e0b',
      nodeType: 'Issue',
    },
    {
      label: 'Processes',
      count: counts.Process,
      icon: <GitFork className="w-4 h-4" />,
      color: '#ec4899',
      nodeType: 'Process',
    },
  ];

  const totalNodes = workspace.node_count ?? Object.values(counts).reduce<number>((sum, c) => sum + (c ?? 0), 0);
  const totalEdges = workspace.edge_count ?? null;

  const overallQuality = quality?.overall_quality;
  const qColor = overallQuality !== undefined ? qualityColor(overallQuality) : '#71717a';
  const completeness = quality?.completeness;

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Conflict Intelligence Stats
            </span>
          </div>
          <h3 className="text-base font-semibold text-zinc-200">{workspace.name}</h3>
          <div className="flex items-center gap-2 text-[11px] text-zinc-500 flex-wrap">
            <span className="capitalize">{workspace.domain}</span>
            <span className="text-zinc-700">·</span>
            <span className="capitalize">{workspace.scale}</span>
            <span className="text-zinc-700">·</span>
            <span
              className={[
                'rounded px-1.5 py-0.5 border text-[10px] font-medium capitalize',
                workspace.status === 'active'
                  ? 'bg-green-600/15 text-green-400 border-green-600/30'
                  : 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30',
              ].join(' ')}
            >
              {workspace.status}
            </span>
          </div>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="p-1.5 rounded-lg border border-[#27272a] bg-zinc-900/50 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600/60 transition-colors disabled:opacity-50"
          title="Refresh stats"
        >
          <RefreshCw className={['w-3.5 h-3.5', loading ? 'animate-spin' : ''].join(' ')} />
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-xs text-red-400 flex items-center gap-2">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
          {error}
        </div>
      )}

      {/* Stat cards grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {statItems.map((item) => (
          <StatCard key={item.label} item={item} loading={loading} />
        ))}
      </div>

      {/* Total nodes/edges row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg border border-[#27272a] bg-zinc-900/30 px-4 py-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2 text-zinc-400">
            <Layers className="w-4 h-4" />
            <span className="text-xs font-medium">Total Nodes</span>
          </div>
          <span className="text-base font-bold text-zinc-200 tabular-nums">
            {loading ? (
              <span className="inline-block w-8 h-5 bg-zinc-800 rounded animate-pulse" />
            ) : (
              totalNodes
            )}
          </span>
        </div>
        <div className="rounded-lg border border-[#27272a] bg-zinc-900/30 px-4 py-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2 text-zinc-400">
            <GitFork className="w-4 h-4" />
            <span className="text-xs font-medium">Total Edges</span>
          </div>
          <span className="text-base font-bold text-zinc-200 tabular-nums">
            {loading ? (
              <span className="inline-block w-8 h-5 bg-zinc-800 rounded animate-pulse" />
            ) : totalEdges !== null ? (
              totalEdges
            ) : (
              '—'
            )}
          </span>
        </div>
      </div>

      {/* Graph quality section */}
      <div className="border-t border-[#27272a] pt-4 space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Graph Quality
            </span>
          </div>
          {completeness?.tier && (
            <span
              className={[
                'inline-block rounded border px-2 py-0.5 text-[10px] font-semibold capitalize',
                tierBadgeClass(completeness.tier),
              ].join(' ')}
            >
              {completeness.tier}
            </span>
          )}
        </div>

        {loading && (
          <div className="space-y-2">
            <div className="h-2 bg-zinc-800 rounded animate-pulse" />
            <div className="h-3 bg-zinc-800 rounded w-1/3 animate-pulse" />
          </div>
        )}

        {!loading && overallQuality !== undefined && (
          <div className="space-y-2">
            {/* Quality bar */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-400">Overall Quality</span>
                <span className="font-bold tabular-nums" style={{ color: qColor }}>
                  {Math.round(overallQuality * 100)}%
                </span>
              </div>
              <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${Math.round(overallQuality * 100)}%`,
                    backgroundColor: qColor,
                  }}
                />
              </div>
            </div>

            {/* Sub-scores */}
            {quality && (
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: 'Completeness', score: quality.completeness.score },
                  { label: 'Consistency', score: quality.consistency.score },
                  { label: 'Coverage', score: quality.coverage.score },
                ].map(({ label, score }) => {
                  const c = qualityColor(score);
                  return (
                    <div
                      key={label}
                      className="rounded-lg border border-[#27272a] bg-zinc-900/40 px-2 py-2 text-center"
                    >
                      <p className="text-[10px] text-zinc-500 font-medium">{label}</p>
                      <p className="text-sm font-bold tabular-nums" style={{ color: c }}>
                        {Math.round(score * 100)}%
                      </p>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Missing node types warning */}
            {completeness && completeness.missing_node_types.length > 0 && (
              <div className="rounded-lg border border-amber-600/20 bg-amber-600/5 px-3 py-2 space-y-1">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-amber-600">
                  Missing Node Types
                </p>
                <div className="flex flex-wrap gap-1">
                  {completeness.missing_node_types.map((t) => (
                    <span
                      key={t}
                      className="inline-block rounded border border-amber-600/30 bg-amber-600/10 text-amber-400 px-1.5 py-0.5 text-[10px]"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {quality && quality.recommendations.length > 0 && (
              <div className="space-y-1">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
                  Recommendations
                </p>
                <ul className="space-y-1">
                  {quality.recommendations.slice(0, 3).map((rec, i) => (
                    <li key={i} className="flex items-start gap-2 text-[11px] text-zinc-400">
                      <span className="text-teal-600 shrink-0 mt-0.5">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {!loading && overallQuality === undefined && (
          <p className="text-xs text-zinc-600 italic">Quality assessment not available</p>
        )}
      </div>
    </div>
  );
}

export default ConflictStats;
