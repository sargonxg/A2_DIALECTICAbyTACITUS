"use client";

import type { AnalysisResult } from "@/types/api";
import { Brain, AlertTriangle, HelpCircle, Lightbulb } from "lucide-react";

interface Props {
  result: AnalysisResult;
}

export default function QueryResult({ result }: Props) {
  return (
    <div className="card space-y-4 animate-fade-in">
      <div className="flex items-center gap-2">
        <Brain size={16} className="text-accent" />
        <span className="badge bg-accent/10 text-accent text-[10px]">{result.mode}</span>
        <span className="text-xs text-text-secondary font-mono">{(result.confidence * 100).toFixed(0)}% confidence</span>
      </div>

      <div className="prose-sm">
        <p className="text-text-primary text-sm leading-relaxed whitespace-pre-wrap">{result.assessment}</p>
      </div>

      {result.evidence.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">Evidence</h4>
          <ul className="space-y-1">
            {result.evidence.map((e, i) => (
              <li key={i} className="text-sm text-text-secondary flex gap-2">
                <span className="text-accent">&bull;</span> {e}
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.theory_lens && (
        <div className="bg-accent/5 border border-accent/20 rounded-md p-3">
          <h4 className="text-xs font-semibold text-accent mb-1 flex items-center gap-1"><Lightbulb size={12} /> Theory Lens</h4>
          <p className="text-sm text-text-primary">{result.theory_lens}</p>
        </div>
      )}

      {result.gaps.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1 flex items-center gap-1"><AlertTriangle size={12} /> Gaps</h4>
          <ul className="space-y-1">
            {result.gaps.map((g, i) => (
              <li key={i} className="text-sm text-warning">{g}</li>
            ))}
          </ul>
        </div>
      )}

      {result.suggested_questions.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1 flex items-center gap-1"><HelpCircle size={12} /> Follow-up</h4>
          <div className="flex flex-wrap gap-1">
            {result.suggested_questions.map((q, i) => (
              <span key={i} className="badge bg-surface-hover text-text-secondary cursor-pointer hover:text-text-primary">{q}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
