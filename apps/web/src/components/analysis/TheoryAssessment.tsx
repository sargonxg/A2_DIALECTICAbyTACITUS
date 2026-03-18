"use client";

import type { TheoryMatch } from "@/types/analysis";
import { BookOpen } from "lucide-react";

interface Props {
  matches: TheoryMatch[];
}

export default function TheoryAssessment({ matches }: Props) {
  const sorted = [...matches].sort((a, b) => b.relevance_score - a.relevance_score);

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
        <BookOpen size={14} className="inline mr-1" /> Theory Assessment
      </h3>
      <div className="space-y-3">
        {sorted.map((match) => (
          <div key={match.framework_id} className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-text-primary">{match.framework_name}</span>
              <span className="font-mono text-xs text-accent">{(match.relevance_score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-1.5 bg-surface-hover rounded-full">
              <div className="h-full bg-accent rounded-full" style={{ width: `${match.relevance_score * 100}%` }} />
            </div>
            <p className="text-xs text-text-secondary">{match.guidance}</p>
            <div className="flex gap-1 flex-wrap">
              {match.matching_patterns.map((p, i) => (
                <span key={i} className="badge bg-accent/10 text-accent text-[10px]">{p}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
