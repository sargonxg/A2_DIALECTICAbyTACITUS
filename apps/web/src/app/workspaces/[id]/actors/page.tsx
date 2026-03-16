'use client';

import { useState, useMemo } from 'react';
import { useParams } from 'next/navigation';
import {
  Users,
  Search,
  Loader2,
  AlertCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  User,
} from 'lucide-react';
import { useGraphData } from '@/hooks/useGraph';
import type { GraphNode } from '@/lib/api';
import { NodeDetail } from '@/components/graph/NodeDetail';

// ─── Actor type badge colors ───────────────────────────────────────────────────

const ACTOR_TYPE_COLORS: Record<string, string> = {
  state:         'bg-blue-500/15 text-blue-400 border-blue-500/30',
  non_state:     'bg-orange-500/15 text-orange-400 border-orange-500/30',
  individual:    'bg-violet-500/15 text-violet-400 border-violet-500/30',
  organisation:  'bg-teal-500/15 text-teal-400 border-teal-500/30',
  organization:  'bg-teal-500/15 text-teal-400 border-teal-500/30',
  militia:       'bg-red-500/15 text-red-400 border-red-500/30',
  ngo:           'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  media:         'bg-pink-500/15 text-pink-400 border-pink-500/30',
  international: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
};

function actorTypeBadge(type: string): string {
  return ACTOR_TYPE_COLORS[type?.toLowerCase()] ?? 'bg-zinc-700/50 text-zinc-400 border-zinc-600/30';
}

// ─── Table row ────────────────────────────────────────────────────────────────

function ActorRow({
  node,
  selected,
  onClick,
}: {
  node: GraphNode;
  selected: boolean;
  onClick: () => void;
}) {
  const props = node.properties ?? {};
  const actorType  = typeof props.actor_type === 'string' ? props.actor_type : '';
  const side       = typeof props.side        === 'string' ? props.side       : '';
  const capabilities = Array.isArray(props.capabilities)
    ? (props.capabilities as string[])
    : typeof props.capabilities === 'string'
    ? [props.capabilities]
    : [];

  return (
    <tr
      onClick={onClick}
      className={`border-b border-[#27272a]/50 cursor-pointer transition-colors ${
        selected
          ? 'bg-violet-500/10 hover:bg-violet-500/15'
          : 'hover:bg-zinc-800/30'
      }`}
    >
      {/* Name */}
      <td className="py-3 px-4">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center shrink-0">
            <User className="w-3 h-3 text-blue-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-zinc-200 truncate">{node.name || node.id}</p>
            <p className="text-[10px] text-zinc-600 font-mono truncate">{node.id}</p>
          </div>
        </div>
      </td>

      {/* Actor type */}
      <td className="py-3 px-4">
        {actorType ? (
          <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest ${actorTypeBadge(actorType)}`}>
            {actorType.replace(/_/g, ' ')}
          </span>
        ) : (
          <span className="text-xs text-zinc-600">—</span>
        )}
      </td>

      {/* Side */}
      <td className="py-3 px-4">
        {side ? (
          <span className="text-xs text-zinc-400 capitalize">{side}</span>
        ) : (
          <span className="text-xs text-zinc-600">—</span>
        )}
      </td>

      {/* Capabilities */}
      <td className="py-3 px-4">
        {capabilities.length > 0 ? (
          <div className="flex flex-wrap gap-1">
            {capabilities.slice(0, 3).map((cap) => (
              <span
                key={cap}
                className="rounded bg-zinc-800 border border-zinc-700/50 px-1.5 py-0.5 text-[10px] text-zinc-400"
              >
                {cap}
              </span>
            ))}
            {capabilities.length > 3 && (
              <span className="text-[10px] text-zinc-600 self-center">+{capabilities.length - 3}</span>
            )}
          </div>
        ) : (
          <span className="text-xs text-zinc-600">—</span>
        )}
      </td>
    </tr>
  );
}

// ─── Page ──────────────────────────────────────────────────────────────────────

type SortKey = 'name' | 'actor_type' | 'side';

export default function ActorsPage() {
  const params = useParams();
  const id = params.id as string;

  const { nodes, loading, error, refetch } = useGraphData(id);

  const [search,      setSearch]      = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [sortKey,     setSortKey]     = useState<SortKey>('name');
  const [sortAsc,     setSortAsc]     = useState(true);

  // Filter to actor nodes only
  const actors = useMemo(
    () => nodes.filter((n) => n.label.toLowerCase() === 'actor'),
    [nodes],
  );

  const filtered = useMemo(() => {
    let list = actors;
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (n) =>
          (n.name ?? '').toLowerCase().includes(q) ||
          n.id.toLowerCase().includes(q) ||
          String(n.properties?.actor_type ?? '').toLowerCase().includes(q),
      );
    }
    return [...list].sort((a, b) => {
      let av = '';
      let bv = '';
      if (sortKey === 'name') {
        av = (a.name ?? a.id).toLowerCase();
        bv = (b.name ?? b.id).toLowerCase();
      } else if (sortKey === 'actor_type') {
        av = String(a.properties?.actor_type ?? '').toLowerCase();
        bv = String(b.properties?.actor_type ?? '').toLowerCase();
      } else {
        av = String(a.properties?.side ?? '').toLowerCase();
        bv = String(b.properties?.side ?? '').toLowerCase();
      }
      const cmp = av.localeCompare(bv);
      return sortAsc ? cmp : -cmp;
    });
  }, [actors, search, sortKey, sortAsc]);

  function handleSort(key: SortKey) {
    if (sortKey === key) setSortAsc((v) => !v);
    else { setSortKey(key); setSortAsc(true); }
  }

  function SortIcon({ col }: { col: SortKey }) {
    if (sortKey !== col) return null;
    return sortAsc
      ? <ChevronUp className="w-3 h-3 inline ml-0.5" />
      : <ChevronDown className="w-3 h-3 inline ml-0.5" />;
  }

  return (
    <div className="flex h-full min-h-0">
      {/* Main content */}
      <div className="flex-1 min-w-0 p-6 space-y-5 overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-zinc-400" />
            <div>
              <h2 className="text-lg font-semibold text-zinc-100">Actors</h2>
              <p className="text-sm text-zinc-500">
                {loading ? 'Loading…' : `${actors.length} actor${actors.length !== 1 ? 's' : ''} in workspace`}
              </p>
            </div>
          </div>
          <button
            onClick={refetch}
            disabled={loading}
            className="p-2 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-[#27272a] transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Search */}
        <div className="relative max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search actors…"
            className="w-full rounded-lg border border-[#27272a] bg-[#18181b] pl-9 pr-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
          />
        </div>

        {/* States */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-7 h-7 text-violet-500 animate-spin" />
          </div>
        )}

        {!loading && error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <p className="text-sm text-zinc-400">{error}</p>
          </div>
        )}

        {!loading && !error && actors.length === 0 && (
          <div className="rounded-xl border border-dashed border-[#27272a] p-12 text-center">
            <Users className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
            <p className="text-sm text-zinc-600">No actor nodes found in this workspace.</p>
          </div>
        )}

        {!loading && !error && filtered.length === 0 && actors.length > 0 && (
          <p className="text-sm text-zinc-600">No actors match your search.</p>
        )}

        {!loading && !error && filtered.length > 0 && (
          <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#27272a]">
                  {(
                    [
                      { key: 'name' as SortKey, label: 'Name' },
                      { key: 'actor_type' as SortKey, label: 'Type' },
                      { key: 'side' as SortKey, label: 'Side' },
                    ] as const
                  ).map((col) => (
                    <th
                      key={col.key}
                      onClick={() => handleSort(col.key)}
                      className="text-left py-3 px-4 text-xs font-semibold uppercase tracking-widest text-zinc-500 cursor-pointer hover:text-zinc-300 select-none transition-colors"
                    >
                      {col.label}
                      <SortIcon col={col.key} />
                    </th>
                  ))}
                  <th className="text-left py-3 px-4 text-xs font-semibold uppercase tracking-widest text-zinc-500">
                    Capabilities
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((node) => (
                  <ActorRow
                    key={node.id}
                    node={node}
                    selected={selectedNode?.id === node.id}
                    onClick={() =>
                      setSelectedNode(selectedNode?.id === node.id ? null : node)
                    }
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail panel */}
      {selectedNode && (
        <div className="w-72 shrink-0 border-l border-[#27272a] p-3 overflow-y-auto">
          <NodeDetail node={selectedNode} onClose={() => setSelectedNode(null)} />
        </div>
      )}
    </div>
  );
}
