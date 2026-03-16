'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Scale, RefreshCw, AlertCircle, Flag, Shield, TrendingUp } from 'lucide-react';
import { graphApi, type GraphNode } from '@/lib/api';

interface InterestOverlapProps {
  workspaceId: string;
}

interface InterestNode {
  id: string;
  name: string;
  description: string;
  actor: string;
  priority: number | null;
  batna_strength: string | null;
  category: string | null;
  shared: boolean;
}

// Priority colours
function priorityColor(p: number | null): string {
  if (p === null) return '#71717a';
  if (p >= 8) return '#ef4444';
  if (p >= 5) return '#eab308';
  return '#22c55e';
}

function priorityLabel(p: number | null): string {
  if (p === null) return 'Unknown';
  if (p >= 8) return 'Critical';
  if (p >= 5) return 'High';
  if (p >= 3) return 'Medium';
  return 'Low';
}

function batnaClass(strength: string | null): string {
  if (!strength) return 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30';
  const s = strength.toLowerCase();
  if (s === 'strong' || s === 'high') return 'bg-green-600/20 text-green-400 border-green-600/30';
  if (s === 'medium' || s === 'moderate') return 'bg-yellow-600/20 text-yellow-400 border-yellow-600/30';
  return 'bg-red-600/20 text-red-400 border-red-600/30';
}

function extractInterestNodes(nodes: GraphNode[]): InterestNode[] {
  return nodes.map((n) => {
    const p = n.properties;
    const priority = typeof p.priority === 'number' ? p.priority : typeof p.priority === 'string' ? parseFloat(p.priority) || null : null;
    const actorName =
      (p.actor_name as string | undefined) ??
      (p.actor as string | undefined) ??
      (p.source_actor as string | undefined) ??
      'Unknown';
    return {
      id: n.id,
      name: n.name || (p.title as string | undefined) || (p.label as string | undefined) || n.label,
      description: (p.description as string | undefined) ?? (p.content as string | undefined) ?? '',
      actor: actorName,
      priority: isNaN(priority as number) ? null : priority,
      batna_strength: (p.batna_strength as string | undefined) ?? (p.batna as string | undefined) ?? null,
      category: (p.category as string | undefined) ?? (p.type as string | undefined) ?? null,
      shared: Boolean(p.shared),
    };
  });
}

function InterestCard({ interest }: { interest: InterestNode }) {
  const pColor = priorityColor(interest.priority);
  return (
    <div className="rounded-lg border border-[#27272a] bg-zinc-900/40 p-3 space-y-2 hover:border-zinc-600/50 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs font-semibold text-zinc-200 leading-snug">{interest.name}</p>
        {interest.priority !== null && (
          <span
            className="shrink-0 inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-semibold"
            style={{
              color: pColor,
              borderColor: `${pColor}40`,
              backgroundColor: `${pColor}15`,
            }}
          >
            <Flag className="w-2.5 h-2.5" />
            P{interest.priority} · {priorityLabel(interest.priority)}
          </span>
        )}
      </div>

      {interest.description && (
        <p className="text-[11px] text-zinc-500 leading-relaxed line-clamp-2">
          {interest.description}
        </p>
      )}

      <div className="flex flex-wrap gap-1.5 items-center">
        {interest.category && (
          <span className="inline-block rounded bg-zinc-800 text-zinc-400 border border-zinc-700/50 px-1.5 py-0.5 text-[10px]">
            {interest.category}
          </span>
        )}
        {interest.batna_strength && (
          <span
            className={[
              'inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-medium',
              batnaClass(interest.batna_strength),
            ].join(' ')}
          >
            <Shield className="w-2.5 h-2.5" />
            BATNA: {interest.batna_strength}
          </span>
        )}
        {interest.shared && (
          <span className="inline-block rounded border border-teal-600/30 bg-teal-600/10 text-teal-400 px-1.5 py-0.5 text-[10px] font-medium">
            Shared
          </span>
        )}
      </div>
    </div>
  );
}

export function InterestOverlap({ workspaceId }: InterestOverlapProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphApi.getNodes(workspaceId, 'Interest');
      setNodes(result.nodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load interest nodes');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  const interests = extractInterestNodes(nodes);

  // Group by actor
  const actorMap: Record<string, InterestNode[]> = {};
  interests.forEach((i) => {
    if (!actorMap[i.actor]) actorMap[i.actor] = [];
    actorMap[i.actor].push(i);
  });

  const actors = Object.entries(actorMap).sort(([, a], [, b]) => b.length - a.length);
  const [sideA, sideB] = actors.length >= 2 ? [actors[0], actors[1]] : [actors[0], null];

  // Shared interests
  const sharedInterests = interests.filter((i) => i.shared);

  // Average priority per actor
  function avgPriority(list: InterestNode[]): number | null {
    const nums = list.map((i) => i.priority).filter((p): p is number => p !== null);
    if (nums.length === 0) return null;
    return nums.reduce((a, b) => a + b, 0) / nums.length;
  }

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Interest Overlap
            </span>
          </div>
          <p className="text-sm text-zinc-400">Fisher–Ury interests, priorities, and BATNA</p>
        </div>
        <div className="flex items-center gap-2">
          {!loading && (
            <span className="text-xs text-zinc-500">
              {interests.length} interest{interests.length !== 1 ? 's' : ''}
            </span>
          )}
          <button
            onClick={load}
            disabled={loading}
            className="p-1.5 rounded-lg border border-[#27272a] bg-zinc-900/50 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600/60 transition-colors disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw className={['w-3.5 h-3.5', loading ? 'animate-spin' : ''].join(' ')} />
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="grid sm:grid-cols-2 gap-4">
          {[1, 2].map((col) => (
            <div key={col} className="space-y-3">
              <div className="h-5 bg-zinc-800 rounded w-1/3 animate-pulse" />
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="rounded-lg border border-[#27272a] bg-zinc-900/40 p-3 space-y-2 animate-pulse"
                >
                  <div className="h-3.5 bg-zinc-800 rounded w-3/4" />
                  <div className="h-3 bg-zinc-800 rounded w-full" />
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-sm font-medium text-red-400">Failed to load interests</p>
            <p className="text-xs text-zinc-500">{error}</p>
            <button
              onClick={load}
              className="text-xs text-teal-400 hover:text-teal-300 font-medium transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && interests.length === 0 && (
        <div className="rounded-lg border border-[#27272a] bg-zinc-900/30 px-4 py-8 text-center space-y-2">
          <Scale className="w-8 h-8 text-zinc-600 mx-auto" />
          <p className="text-sm font-medium text-zinc-500">No interest nodes found</p>
          <p className="text-xs text-zinc-600">Add Interest nodes to compare actor positions.</p>
        </div>
      )}

      {/* Two-column comparison */}
      {!loading && !error && interests.length > 0 && (
        <>
          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-lg border border-[#27272a] bg-zinc-900/40 px-3 py-2 text-center">
              <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">Actors</p>
              <p className="text-lg font-bold text-zinc-200">{actors.length}</p>
            </div>
            <div className="rounded-lg border border-[#27272a] bg-zinc-900/40 px-3 py-2 text-center">
              <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">Interests</p>
              <p className="text-lg font-bold text-zinc-200">{interests.length}</p>
            </div>
            <div className="rounded-lg border border-teal-600/20 bg-teal-600/5 px-3 py-2 text-center">
              <p className="text-[10px] uppercase tracking-widest text-teal-600 font-medium">Shared</p>
              <p className="text-lg font-bold text-teal-400">{sharedInterests.length}</p>
            </div>
          </div>

          {/* Side comparison (primary two actors) */}
          {sideA && sideB && (
            <div className="grid sm:grid-cols-2 gap-4">
              {[sideA, sideB].map(([actor, list], colIdx) => {
                const avg = avgPriority(list);
                const avgColor = priorityColor(avg);
                return (
                  <div key={actor} className="space-y-2">
                    {/* Actor header */}
                    <div
                      className={[
                        'flex items-center justify-between rounded-lg border px-3 py-2',
                        colIdx === 0
                          ? 'border-blue-600/30 bg-blue-600/10'
                          : 'border-orange-600/30 bg-orange-600/10',
                      ].join(' ')}
                    >
                      <div>
                        <p
                          className={[
                            'text-xs font-bold',
                            colIdx === 0 ? 'text-blue-400' : 'text-orange-400',
                          ].join(' ')}
                        >
                          {actor}
                        </p>
                        <p className="text-[10px] text-zinc-500">
                          {list.length} interest{list.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                      {avg !== null && (
                        <div className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" style={{ color: avgColor }} />
                          <span
                            className="text-[11px] font-semibold"
                            style={{ color: avgColor }}
                          >
                            P{avg.toFixed(1)}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Interest cards */}
                    <div className="space-y-2">
                      {list
                        .sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0))
                        .map((interest) => (
                          <InterestCard key={interest.id} interest={interest} />
                        ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Additional actors (beyond first two) */}
          {actors.length > 2 && (
            <div className="space-y-2">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
                Other Actors
              </p>
              <div className="grid sm:grid-cols-2 gap-3">
                {actors.slice(2).map(([actor, list]) => (
                  <div key={actor} className="space-y-2">
                    <div className="flex items-center justify-between rounded-lg border border-[#27272a] bg-zinc-900/40 px-3 py-2">
                      <p className="text-xs font-semibold text-zinc-300">{actor}</p>
                      <span className="text-[11px] text-zinc-500">
                        {list.length} interest{list.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    {list.slice(0, 3).map((interest) => (
                      <InterestCard key={interest.id} interest={interest} />
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Shared interests */}
          {sharedInterests.length > 0 && (
            <>
              <div className="border-t border-[#27272a]" />
              <div className="space-y-2">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
                  Shared Interests (Zone of Possible Agreement)
                </p>
                <div className="grid sm:grid-cols-2 gap-2">
                  {sharedInterests.map((interest) => (
                    <InterestCard key={interest.id} interest={interest} />
                  ))}
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default InterestOverlap;
