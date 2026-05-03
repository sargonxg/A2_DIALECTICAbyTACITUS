import { RefreshCcw } from "lucide-react";
import type { CuratedReasoningQuestion } from "./types";

interface Props {
  question: CuratedReasoningQuestion;
  active: boolean;
  onToggle: () => void;
}

export function CounterfactualToggler({ question, active, onToggle }: Props) {
  if (!question.counterfactual_supported || !question.counterfactual) {
    return (
      <div className="rounded-lg border border-border bg-surface p-3 text-sm text-text-secondary">
        Counterfactuals are disabled for this question because the supported intervention would require a larger graph mutation than the demo keeps in memory.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
        <RefreshCcw className="h-4 w-4 text-amber-300" aria-hidden="true" />
        Counterfactual
      </div>
      <p className="text-xs leading-5 text-text-secondary">
        Transient graph mutilation only. Nothing is written back to Neo4j.
      </p>
      <button
        type="button"
        data-test="counterfactual-toggle"
        onClick={onToggle}
        className={`mt-3 w-full rounded-md border px-3 py-2 text-sm font-semibold transition-colors ${
          active
            ? "border-amber-400 bg-amber-400/15 text-amber-100"
            : "border-border bg-background text-text-primary hover:bg-surface-hover"
        }`}
      >
        {active ? "Clear counterfactual" : question.counterfactual.remove_label}
      </button>
    </div>
  );
}
