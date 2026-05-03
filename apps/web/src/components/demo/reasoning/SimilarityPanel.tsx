import { GitBranch } from "lucide-react";
import type { CuratedReasoningQuestion } from "./types";

interface Props {
  question: CuratedReasoningQuestion;
}

export function SimilarityPanel({ question }: Props) {
  if (!question.similarity_supported || !question.similarity?.length) {
    return (
      <div className="rounded-lg border border-border bg-surface p-3 text-sm text-text-secondary">
        Structural similarity is not attached to this question.
      </div>
    );
  }

  return (
    <section className="rounded-lg border border-border bg-surface p-3">
      <div className="mb-3 flex items-center gap-2">
        <GitBranch className="h-4 w-4 text-cyan-300" aria-hidden="true" />
        <h3 className="text-sm font-semibold text-text-primary">Nearest structural neighbours</h3>
      </div>
      <div className="space-y-2">
        {question.similarity.map((item, index) => (
          <article key={item.workspace_id} className="rounded-md border border-border bg-background p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-xs text-accent">#{index + 1} · {item.workspace_id}</p>
                <h4 className="mt-1 text-sm font-semibold text-text-primary">{item.conflict_name}</h4>
              </div>
              <span className="rounded-md bg-cyan-500/10 px-2 py-1 font-mono text-xs text-cyan-200">
                d={item.combined_dist.toFixed(2)}
              </span>
            </div>
            <p className="mt-2 text-xs leading-5 text-text-secondary">{item.explanation}</p>
            <div className="mt-2 grid grid-cols-3 gap-2 text-[11px] text-text-secondary">
              <span>semantic {item.semantic_dist.toFixed(2)}</span>
              <span>topology {item.topological_dist.toFixed(2)}</span>
              <span>combined {item.combined_dist.toFixed(2)}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
