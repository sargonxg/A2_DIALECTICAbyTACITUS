"use client";

import { cn } from "@/lib/utils";
import type { TheoryAssessment } from "@/types/api";

interface TheoryGridProps {
  assessments: TheoryAssessment[];
}

function scoreColor(score: number): string {
  if (score > 0.7) return "text-emerald-400";
  if (score > 0.4) return "text-amber-400";
  return "text-zinc-500";
}

function progressColor(score: number): string {
  if (score > 0.7) return "bg-emerald-500";
  if (score > 0.4) return "bg-amber-500";
  return "bg-zinc-600";
}

function domainBadgeColor(domain: string): string {
  const map: Record<string, string> = {
    geopolitical: "bg-blue-950 text-blue-300 border-blue-800",
    workplace: "bg-purple-950 text-purple-300 border-purple-800",
    commercial: "bg-orange-950 text-orange-300 border-orange-800",
    legal: "bg-slate-900 text-slate-300 border-slate-700",
    armed: "bg-red-950 text-red-300 border-red-800",
    environmental: "bg-green-950 text-green-300 border-green-800",
    human_friction: "bg-violet-950 text-violet-300 border-violet-800",
    conflict_warfare: "bg-rose-950 text-rose-300 border-rose-800",
    universal: "bg-zinc-900 text-zinc-400 border-zinc-700",
  };
  return map[domain.toLowerCase()] ?? "bg-zinc-900 text-zinc-400 border-zinc-700";
}

function TheoryCard({ assessment }: { assessment: TheoryAssessment }) {
  const pct = Math.round(assessment.score * 100);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3 hover:border-zinc-700 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-white leading-tight flex-1">
          {assessment.display_name}
        </h3>
        <span
          className={cn(
            "shrink-0 text-[10px] px-1.5 py-0.5 rounded border font-medium capitalize",
            domainBadgeColor(assessment.domain),
          )}
        >
          {assessment.domain.replace("_", " ")}
        </span>
      </div>

      {/* Score bar */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-zinc-500">Applicability</span>
          <span className={cn("text-xs font-bold tabular-nums", scoreColor(assessment.score))}>
            {pct}%
          </span>
        </div>
        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all duration-500", progressColor(assessment.score))}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Primary questions */}
      {assessment.primary_questions.length > 0 && (
        <div>
          <p className="text-[10px] text-zinc-600 uppercase tracking-wider font-semibold mb-1">
            Key questions
          </p>
          <ul className="space-y-0.5">
            {assessment.primary_questions.slice(0, 2).map((q, i) => (
              <li key={i} className="text-xs text-zinc-400 flex gap-1.5 items-start">
                <span className="text-zinc-600 shrink-0 mt-0.5">›</span>
                <span className="leading-snug">{q}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Key propositions */}
      {assessment.key_propositions.length > 0 && (
        <div>
          <p className="text-[10px] text-zinc-600 uppercase tracking-wider font-semibold mb-1">
            Propositions matched
          </p>
          <div className="flex flex-wrap gap-1">
            {assessment.key_propositions.slice(0, 3).map((p, i) => (
              <span
                key={i}
                className="text-[9px] bg-zinc-800 text-zinc-400 rounded px-1.5 py-0.5 truncate max-w-[120px]"
                title={p}
              >
                {p}
              </span>
            ))}
            {assessment.key_propositions.length > 3 && (
              <span className="text-[9px] text-zinc-600">
                +{assessment.key_propositions.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function TheoryGrid({ assessments }: TheoryGridProps) {
  if (assessments.length === 0) {
    return (
      <div className="text-center py-16 text-zinc-600 text-sm">
        No theory assessments available for this workspace.
      </div>
    );
  }

  // Sort by score descending
  const sorted = [...assessments].sort((a, b) => b.score - a.score);

  const highRelevance = sorted.filter((a) => a.score > 0.7);
  const medRelevance = sorted.filter((a) => a.score > 0.4 && a.score <= 0.7);
  const lowRelevance = sorted.filter((a) => a.score <= 0.4);

  return (
    <div className="space-y-6">
      {highRelevance.length > 0 && (
        <section>
          <h3 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3">
            High relevance ({highRelevance.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {highRelevance.map((a) => (
              <TheoryCard key={a.framework_id} assessment={a} />
            ))}
          </div>
        </section>
      )}

      {medRelevance.length > 0 && (
        <section>
          <h3 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-3">
            Moderate relevance ({medRelevance.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {medRelevance.map((a) => (
              <TheoryCard key={a.framework_id} assessment={a} />
            ))}
          </div>
        </section>
      )}

      {lowRelevance.length > 0 && (
        <section>
          <h3 className="text-xs font-semibold text-zinc-600 uppercase tracking-wider mb-3">
            Low relevance ({lowRelevance.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {lowRelevance.map((a) => (
              <TheoryCard key={a.framework_id} assessment={a} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
