'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  Compass,
  Search,
  Loader2,
  AlertCircle,
  RefreshCw,
  Filter,
  Layers,
  Network,
  Globe,
} from 'lucide-react';
import { useWorkspaceList } from '@/hooks/useWorkspace';
import type { Workspace } from '@/lib/api';

// ─── Constants ────────────────────────────────────────────────────────────────

const DOMAINS = ['interpersonal', 'workplace', 'commercial', 'legal', 'political', 'armed'];
const SCALES  = ['micro', 'meso', 'macro', 'meta'];

const DOMAIN_COLORS: Record<string, string> = {
  interpersonal: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  workplace:     'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
  commercial:    'bg-green-500/15 text-green-400 border-green-500/30',
  legal:         'bg-orange-500/15 text-orange-400 border-orange-500/30',
  political:     'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
  armed:         'bg-red-500/15 text-red-400 border-red-500/30',
};

const SCALE_COLORS: Record<string, string> = {
  micro:  'bg-violet-500/15 text-violet-400 border-violet-500/30',
  meso:   'bg-purple-500/15 text-purple-400 border-purple-500/30',
  macro:  'bg-pink-500/15 text-pink-400 border-pink-500/30',
  meta:   'bg-rose-500/15 text-rose-400 border-rose-500/30',
};

function glaslColor(stage?: number): string {
  if (stage == null) return 'text-zinc-600';
  if (stage <= 3) return 'text-green-500';
  if (stage <= 6) return 'text-yellow-500';
  return 'text-red-500';
}

function glaslLabel(stage?: number): string {
  if (stage == null) return 'Unknown';
  if (stage <= 3) return `Stage ${stage} — Win-Win`;
  if (stage <= 6) return `Stage ${stage} — Win-Lose`;
  return `Stage ${stage} — Lose-Lose`;
}

// ─── Card ─────────────────────────────────────────────────────────────────────

function ExploreCard({ workspace, onClick }: { workspace: Workspace; onClick: () => void }) {
  const domainCls = DOMAIN_COLORS[workspace.domain] ?? 'bg-zinc-700/50 text-zinc-400 border-zinc-600/30';
  const scaleCls  = SCALE_COLORS[workspace.scale]   ?? 'bg-zinc-700/50 text-zinc-400 border-zinc-600/30';

  return (
    <button
      onClick={onClick}
      className="text-left w-full rounded-xl border border-[#27272a] bg-[#18181b] p-5 hover:border-violet-500/40 hover:bg-[#1c1c1f] transition-all duration-150 focus:outline-none focus:border-violet-500/60 group"
    >
      {/* Name */}
      <h3 className="text-sm font-semibold text-zinc-100 group-hover:text-white truncate mb-3">
        {workspace.name}
      </h3>

      {/* Domain + scale badges */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest ${domainCls}`}>
          {workspace.domain}
        </span>
        <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest ${scaleCls}`}>
          {workspace.scale}
        </span>
        {workspace.status && (
          <span
            className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest ${
              workspace.status === 'active'
                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                : 'bg-zinc-700/50 text-zinc-400 border-zinc-600/30'
            }`}
          >
            {workspace.status}
          </span>
        )}
      </div>

      {/* Conflict stats preview */}
      <div className="rounded-lg border border-[#27272a] bg-zinc-900/30 p-3 space-y-1.5">
        {/* Glasl stage */}
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-widest text-zinc-600 font-medium">Glasl Stage</span>
          <span className={`text-xs font-semibold ${glaslColor(workspace.glasl_stage)}`}>
            {glaslLabel(workspace.glasl_stage)}
          </span>
        </div>

        {/* Kriesberg phase */}
        {workspace.kriesberg_phase && (
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-widest text-zinc-600 font-medium">Phase</span>
            <span className="text-xs text-zinc-400 capitalize">{workspace.kriesberg_phase}</span>
          </div>
        )}

        {/* Node/edge counts */}
        <div className="flex items-center gap-4 pt-1 border-t border-[#27272a]">
          {workspace.node_count != null && (
            <div className="flex items-center gap-1.5">
              <Layers className="w-3 h-3 text-zinc-600" />
              <span className="text-xs text-zinc-500">{workspace.node_count} nodes</span>
            </div>
          )}
          {workspace.edge_count != null && (
            <div className="flex items-center gap-1.5">
              <Network className="w-3 h-3 text-zinc-600" />
              <span className="text-xs text-zinc-500">{workspace.edge_count} edges</span>
            </div>
          )}
        </div>
      </div>
    </button>
  );
}

// ─── Page ──────────────────────────────────────────────────────────────────────

export default function ExplorePage() {
  const router = useRouter();
  const { workspaces, loading, error, refetch } = useWorkspaceList();

  const [search,       setSearch]       = useState('');
  const [filterDomain, setFilterDomain] = useState('');
  const [filterScale,  setFilterScale]  = useState('');

  const filtered = useMemo(() => {
    let list = workspaces;
    if (filterDomain) list = list.filter((w) => w.domain === filterDomain);
    if (filterScale)  list = list.filter((w) => w.scale  === filterScale);
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((w) => w.name.toLowerCase().includes(q));
    }
    return list;
  }, [workspaces, filterDomain, filterScale, search]);

  return (
    <div className="min-h-full p-6 max-w-7xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-violet-500/20 border border-violet-500/30">
            <Compass className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-zinc-100">Explore</h1>
            <p className="text-sm text-zinc-500">Browse all conflict workspaces.</p>
          </div>
        </div>
        <button
          onClick={refetch}
          disabled={loading}
          className="p-2 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-[#27272a] transition-colors disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search workspaces by name…"
            className="w-full rounded-lg border border-[#27272a] bg-[#18181b] pl-9 pr-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
          />
        </div>

        {/* Domain filter */}
        <div className="relative">
          <Globe className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
          <select
            value={filterDomain}
            onChange={(e) => setFilterDomain(e.target.value)}
            className="appearance-none rounded-lg border border-[#27272a] bg-[#18181b] pl-8 pr-7 py-2.5 text-sm text-zinc-100 focus:border-violet-500/60 focus:outline-none transition-colors"
          >
            <option value="">All domains</option>
            {DOMAINS.map((d) => (
              <option key={d} value={d} className="bg-[#18181b] capitalize">{d}</option>
            ))}
          </select>
        </div>

        {/* Scale filter */}
        <div className="relative">
          <Filter className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
          <select
            value={filterScale}
            onChange={(e) => setFilterScale(e.target.value)}
            className="appearance-none rounded-lg border border-[#27272a] bg-[#18181b] pl-8 pr-7 py-2.5 text-sm text-zinc-100 focus:border-violet-500/60 focus:outline-none transition-colors"
          >
            <option value="">All scales</option>
            {SCALES.map((s) => (
              <option key={s} value={s} className="bg-[#18181b] capitalize">{s}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="w-8 h-8 text-violet-500 animate-spin" />
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-zinc-100">Failed to load workspaces</p>
            <p className="text-sm text-zinc-400 mt-1">{error}</p>
            <button onClick={refetch} className="mt-3 text-xs text-violet-400 hover:underline">
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && filtered.length === 0 && (
        <div className="rounded-xl border border-dashed border-[#27272a] p-12 text-center">
          <Compass className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-600">
            {workspaces.length === 0 ? 'No workspaces yet.' : 'No workspaces match your filters.'}
          </p>
        </div>
      )}

      {/* Grid */}
      {!loading && !error && filtered.length > 0 && (
        <>
          <p className="text-xs text-zinc-600">
            {filtered.length} of {workspaces.length} workspace{workspaces.length !== 1 ? 's' : ''}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((ws) => (
              <ExploreCard
                key={ws.id}
                workspace={ws}
                onClick={() => router.push(`/workspaces/${ws.id}`)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
