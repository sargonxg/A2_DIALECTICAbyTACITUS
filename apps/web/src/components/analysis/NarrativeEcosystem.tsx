'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { BookOpen, RefreshCw, AlertCircle, Tag, Radio, Users } from 'lucide-react';
import { graphApi, type GraphNode } from '@/lib/api';

interface NarrativeEcosystemProps {
  workspaceId: string;
}

// Colour palette for frame_type badges
const FRAME_TYPE_COLORS: Record<string, string> = {
  identity: 'bg-purple-600/20 text-purple-400 border-purple-600/30',
  grievance: 'bg-red-600/20 text-red-400 border-red-600/30',
  threat: 'bg-orange-600/20 text-orange-400 border-orange-600/30',
  opportunity: 'bg-green-600/20 text-green-400 border-green-600/30',
  historical: 'bg-amber-600/20 text-amber-400 border-amber-600/30',
  legitimacy: 'bg-blue-600/20 text-blue-400 border-blue-600/30',
  dehumanisation: 'bg-rose-700/20 text-rose-400 border-rose-700/30',
  peace: 'bg-teal-600/20 text-teal-400 border-teal-600/30',
};

function frameTypeBadgeClass(frameType?: string): string {
  if (!frameType) return 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30';
  const key = frameType.toLowerCase();
  return FRAME_TYPE_COLORS[key] ?? 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30';
}

function ScorePill({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value?: number | string | null;
  icon: React.ReactNode;
  color: string;
}) {
  if (value === undefined || value === null) return null;
  const numVal = typeof value === 'string' ? parseFloat(value) : value;
  const display = isNaN(numVal) ? String(value) : `${Math.round(numVal * 100)}%`;
  return (
    <div
      className="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium border"
      style={{ color, borderColor: `${color}40`, backgroundColor: `${color}18` }}
    >
      {icon}
      <span className="text-zinc-400">{label}</span>
      <span style={{ color }}>{display}</span>
    </div>
  );
}

function NarrativeCard({ node }: { node: GraphNode }) {
  const props = node.properties;
  const frameType = props.frame_type as string | undefined;
  const coherence = props.coherence_score ?? props.coherence;
  const reach = props.reach_score ?? props.reach;
  const content =
    (props.content as string) ??
    (props.narrative as string) ??
    (props.description as string) ??
    '';
  const author = props.author as string | undefined;

  return (
    <div className="rounded-lg border border-[#27272a] bg-zinc-900/40 p-4 space-y-3 hover:border-zinc-600/60 transition-colors">
      {/* Top row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0 space-y-0.5">
          <p className="text-sm font-semibold text-zinc-200 truncate">{node.name || node.label}</p>
          {author && (
            <div className="flex items-center gap-1 text-[11px] text-zinc-500">
              <Users className="w-3 h-3" />
              {author}
            </div>
          )}
        </div>
        {frameType && (
          <span
            className={[
              'inline-flex items-center gap-1 rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide shrink-0',
              frameTypeBadgeClass(frameType),
            ].join(' ')}
          >
            <Tag className="w-2.5 h-2.5" />
            {frameType}
          </span>
        )}
      </div>

      {/* Content preview */}
      {content && (
        <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">{content}</p>
      )}

      {/* Scores */}
      <div className="flex flex-wrap gap-1.5">
        <ScorePill
          label="Coherence"
          value={coherence as number | null | undefined}
          icon={<BookOpen className="w-2.5 h-2.5" />}
          color="#0d9488"
        />
        <ScorePill
          label="Reach"
          value={reach as number | null | undefined}
          icon={<Radio className="w-2.5 h-2.5" />}
          color="#6366f1"
        />
      </div>
    </div>
  );
}

export function NarrativeEcosystem({ workspaceId }: NarrativeEcosystemProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphApi.getNodes(workspaceId, 'Narrative');
      setNodes(result.nodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load narrative nodes');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  // Compute frame type distribution
  const frameCounts: Record<string, number> = {};
  nodes.forEach((n) => {
    const ft = (n.properties.frame_type as string | undefined) ?? 'unknown';
    frameCounts[ft] = (frameCounts[ft] ?? 0) + 1;
  });

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Narrative Ecosystem
            </span>
          </div>
          <p className="text-sm text-zinc-400">Competing frames, coherence, and reach</p>
        </div>
        <div className="flex items-center gap-2">
          {!loading && (
            <span className="text-xs text-zinc-500">
              {nodes.length} narrative{nodes.length !== 1 ? 's' : ''}
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

      {/* Frame type distribution */}
      {!loading && !error && Object.keys(frameCounts).length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(frameCounts).map(([ft, count]) => (
            <span
              key={ft}
              className={[
                'inline-flex items-center gap-1 rounded border px-2 py-0.5 text-[11px] font-medium',
                frameTypeBadgeClass(ft),
              ].join(' ')}
            >
              <Tag className="w-2.5 h-2.5" />
              {ft}
              <span className="opacity-60">×{count}</span>
            </span>
          ))}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="rounded-lg border border-[#27272a] bg-zinc-900/40 p-4 space-y-2 animate-pulse"
            >
              <div className="h-4 bg-zinc-800 rounded w-2/3" />
              <div className="h-3 bg-zinc-800 rounded w-full" />
              <div className="h-3 bg-zinc-800 rounded w-4/5" />
              <div className="flex gap-2">
                <div className="h-5 bg-zinc-800 rounded w-20" />
                <div className="h-5 bg-zinc-800 rounded w-16" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-sm font-medium text-red-400">Failed to load narratives</p>
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

      {/* Empty state */}
      {!loading && !error && nodes.length === 0 && (
        <div className="rounded-lg border border-[#27272a] bg-zinc-900/30 px-4 py-8 text-center space-y-2">
          <BookOpen className="w-8 h-8 text-zinc-600 mx-auto" />
          <p className="text-sm font-medium text-zinc-500">No narrative nodes found</p>
          <p className="text-xs text-zinc-600">
            Ingest documents or add Narrative nodes to populate this view.
          </p>
        </div>
      )}

      {/* Narrative cards */}
      {!loading && !error && nodes.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2">
          {nodes.map((node) => (
            <NarrativeCard key={node.id} node={node} />
          ))}
        </div>
      )}
    </div>
  );
}

export default NarrativeEcosystem;
