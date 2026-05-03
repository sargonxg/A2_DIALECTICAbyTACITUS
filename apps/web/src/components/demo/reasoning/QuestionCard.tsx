import { GitBranch, Microscope, RefreshCcw } from "lucide-react";
import type { CuratedReasoningQuestion } from "./types";

interface Props {
  question: CuratedReasoningQuestion;
  active: boolean;
  onSelect: () => void;
}

export function QuestionCard({ question, active, onSelect }: Props) {
  return (
    <button
      type="button"
      data-question={question.id}
      onClick={onSelect}
      className={`w-full rounded-lg border p-3 text-left transition-colors ${
        active
          ? "border-accent bg-accent/10 text-text-primary"
          : "border-border bg-surface text-text-secondary hover:border-border-hover hover:bg-surface-hover"
      }`}
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="font-mono text-xs font-semibold text-accent">{question.id}</span>
        <span className="flex items-center gap-1 text-[10px] uppercase tracking-wide">
          {question.counterfactual_supported && <RefreshCcw className="h-3.5 w-3.5" aria-label="Counterfactual supported" />}
          {question.similarity_supported && <GitBranch className="h-3.5 w-3.5" aria-label="Similarity supported" />}
          <Microscope className="h-3.5 w-3.5" aria-hidden="true" />
        </span>
      </div>
      <p className="text-sm font-semibold leading-5 text-text-primary">{question.text}</p>
      <p className="mt-2 line-clamp-2 text-xs leading-5 text-text-secondary">{question.stake}</p>
    </button>
  );
}
