'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  BookOpen,
  User,
  Calendar,
  ChevronDown,
  Loader2,
  AlertCircle,
  ExternalLink,
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

function domainBadge(domain: string): string {
  return DOMAIN_COLORS[domain.toLowerCase()] ?? 'bg-zinc-700/50 text-zinc-400 border-zinc-600/30';
}

interface AccordionItemProps {
  name: string;
  definition: string;
  index: number;
}

function AccordionItem({ name, definition, index }: AccordionItemProps) {
  const [open, setOpen] = useState(index === 0);

  return (
    <div className="rounded-lg border border-[#27272a] overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left bg-[#18181b] hover:bg-zinc-800/50 transition-colors"
      >
        <span className="text-sm font-medium text-zinc-200">{name}</span>
        <ChevronDown
          className={`w-4 h-4 text-zinc-500 shrink-0 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && (
        <div className="px-4 py-3 border-t border-[#27272a] bg-zinc-900/30">
          <p className="text-sm text-zinc-400 leading-relaxed">{definition}</p>
        </div>
      )}
    </div>
  );
}

export default function TheoryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [framework, setFramework] = useState<Framework | null>(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    theoryApi.getFramework(id)
      .then(setFramework)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="min-h-full p-6 max-w-4xl space-y-6">
      {/* Back button */}
      <button
        onClick={() => router.push('/theory')}
        className="inline-flex items-center gap-1.5 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Theory Frameworks
      </button>

      {/* States */}
      {loading && (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="w-8 h-8 text-violet-500 animate-spin" />
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-zinc-100">Failed to load framework</p>
            <p className="text-sm text-zinc-400 mt-1">{error}</p>
          </div>
        </div>
      )}

      {!loading && !error && framework && (
        <>
          {/* Header card */}
          <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-6 space-y-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-violet-500/20 border border-violet-500/30 shrink-0">
                <BookOpen className="w-5 h-5 text-violet-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h1 className="text-xl font-bold text-zinc-100">{framework.name}</h1>
                {framework.domain && (
                  <span
                    className={`mt-2 inline-block rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest ${domainBadge(framework.domain)}`}
                  >
                    {framework.domain}
                  </span>
                )}
              </div>
            </div>

            {/* Meta */}
            <div className="flex flex-wrap gap-4">
              {framework.author && (
                <div className="flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-zinc-500" />
                  <span className="text-sm text-zinc-400">{framework.author}</span>
                </div>
              )}
              {framework.year && (
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-zinc-500" />
                  <span className="text-sm text-zinc-400">{framework.year}</span>
                </div>
              )}
            </div>

            {/* Summary */}
            {framework.summary && (
              <p className="text-sm text-zinc-300 leading-relaxed border-t border-[#27272a] pt-4">
                {framework.summary}
              </p>
            )}
          </div>

          {/* Key concepts accordion */}
          {framework.key_concepts && framework.key_concepts.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                <ExternalLink className="w-3.5 h-3.5" />
                Key Concepts ({framework.key_concepts.length})
              </h2>
              <div className="space-y-2">
                {framework.key_concepts.map((concept, i) => (
                  <AccordionItem
                    key={concept.name}
                    name={concept.name}
                    definition={concept.definition}
                    index={i}
                  />
                ))}
              </div>
            </div>
          )}

          {/* No key concepts fallback */}
          {(!framework.key_concepts || framework.key_concepts.length === 0) && (
            <div className="rounded-xl border border-dashed border-[#27272a] p-8 text-center">
              <p className="text-sm text-zinc-600">No key concepts defined for this framework.</p>
            </div>
          )}

          {/* Back link at bottom */}
          <div className="pt-4 border-t border-[#27272a]">
            <button
              onClick={() => router.push('/theory')}
              className="inline-flex items-center gap-1.5 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to all frameworks
            </button>
          </div>
        </>
      )}
    </div>
  );
}
