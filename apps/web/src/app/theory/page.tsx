'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  BookOpen,
  Search,
  Loader2,
  AlertCircle,
  ChevronRight,
  Filter,
} from 'lucide-react';
import { theoryApi, type Framework } from '@/lib/api';

const DOMAIN_COLORS: Record<string, string> = {
  negotiation:   'bg-blue-500/15 text-blue-400 border-blue-500/30',
  mediation:     'bg-teal-500/15 text-teal-400 border-teal-500/30',
  escalation:    'bg-red-500/15 text-red-400 border-red-500/30',
  ripeness:      'bg-green-500/15 text-green-400 border-green-500/30',
  peacebuilding: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  power:         'bg-orange-500/15 text-orange-400 border-orange-500/30',
  identity:      'bg-purple-500/15 text-purple-400 border-purple-500/30',
  trust:         'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
};

function domainBadgeClass(domain: string): string {
  return DOMAIN_COLORS[domain.toLowerCase()] ?? 'bg-zinc-700/50 text-zinc-400 border-zinc-600/30';
}

function FrameworkCard({ framework, onClick }: { framework: Framework; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-left w-full rounded-xl border border-[#27272a] bg-[#18181b] p-5 hover:border-violet-500/40 hover:bg-[#1c1c1f] transition-all duration-150 group focus:outline-none focus:border-violet-500/60"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-zinc-100 group-hover:text-white truncate">
            {framework.name}
          </h3>
          <p className="text-xs text-zinc-500 mt-0.5">
            {framework.author}
            {framework.year ? ` · ${framework.year}` : ''}
          </p>
        </div>
        <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 shrink-0 mt-0.5 transition-colors" />
      </div>

      {framework.domain && (
        <span
          className={`inline-block rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest mb-3 ${domainBadgeClass(framework.domain)}`}
        >
          {framework.domain}
        </span>
      )}

      {framework.summary && (
        <p className="text-xs text-zinc-500 leading-relaxed line-clamp-3">{framework.summary}</p>
      )}

      {framework.key_concepts && framework.key_concepts.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {framework.key_concepts.slice(0, 3).map((c) => (
            <span
              key={c.name}
              className="rounded bg-zinc-800 border border-zinc-700/50 px-1.5 py-0.5 text-[10px] text-zinc-400"
            >
              {c.name}
            </span>
          ))}
          {framework.key_concepts.length > 3 && (
            <span className="text-[10px] text-zinc-600 self-center">
              +{framework.key_concepts.length - 3} more
            </span>
          )}
        </div>
      )}
    </button>
  );
}

export default function TheoryPage() {
  const router = useRouter();

  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState<string | null>(null);

  const [search,        setSearch]        = useState('');
  const [filterDomain,  setFilterDomain]  = useState('');

  useEffect(() => {
    theoryApi.listFrameworks()
      .then((res) => setFrameworks(res.frameworks ?? []))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const domains = useMemo(
    () => Array.from(new Set(frameworks.map((f) => f.domain).filter(Boolean))).sort(),
    [frameworks],
  );

  const filtered = useMemo(() => {
    let list = frameworks;
    if (filterDomain) list = list.filter((f) => f.domain === filterDomain);
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (f) =>
          f.name.toLowerCase().includes(q) ||
          f.author.toLowerCase().includes(q) ||
          (f.summary ?? '').toLowerCase().includes(q),
      );
    }
    return list;
  }, [frameworks, filterDomain, search]);

  return (
    <div className="min-h-full p-6 max-w-6xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-violet-500/20 border border-violet-500/30">
          <BookOpen className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-zinc-100">Theory Frameworks</h1>
          <p className="text-sm text-zinc-500">
            Conflict analysis frameworks and theoretical lenses.
          </p>
        </div>
      </div>

      {/* Search + filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search frameworks, authors…"
            className="w-full rounded-lg border border-[#27272a] bg-[#18181b] pl-9 pr-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
          />
        </div>

        {domains.length > 0 && (
          <div className="relative">
            <Filter className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
            <select
              value={filterDomain}
              onChange={(e) => setFilterDomain(e.target.value)}
              className="appearance-none rounded-lg border border-[#27272a] bg-[#18181b] pl-8 pr-8 py-2.5 text-sm text-zinc-100 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
            >
              <option value="">All domains</option>
              {domains.map((d) => (
                <option key={d} value={d} className="bg-[#18181b] capitalize">
                  {d}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* States */}
      {loading && (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="w-8 h-8 text-violet-500 animate-spin" />
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <p className="text-sm text-zinc-400">{error}</p>
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="rounded-xl border border-dashed border-[#27272a] p-12 text-center">
          <BookOpen className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-600">
            {frameworks.length === 0
              ? 'No theory frameworks available yet.'
              : 'No frameworks match your search.'}
          </p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <>
          <p className="text-xs text-zinc-600">
            Showing {filtered.length} of {frameworks.length} framework
            {frameworks.length !== 1 ? 's' : ''}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((fw) => (
              <FrameworkCard
                key={fw.id}
                framework={fw}
                onClick={() => router.push(`/theory/${fw.id}`)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
