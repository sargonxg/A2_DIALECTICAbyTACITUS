import { Clock, Quote } from "lucide-react";
import type { CuratedReasoningQuestion } from "./types";

interface Props {
  question: CuratedReasoningQuestion;
}

export function LLMComparisonPanel({ question }: Props) {
  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Frontier LLM comparison</p>
          <h3 className="mt-1 text-lg font-semibold text-text-primary">{question.llm.model}</h3>
        </div>
        <Quote className="h-5 w-5 text-text-secondary" aria-hidden="true" />
      </div>
      <p className="text-sm leading-6 text-text-secondary">{question.llm.answer}</p>
      <div className="mt-4 grid gap-2 border-t border-border pt-3 text-xs text-text-secondary sm:grid-cols-2">
        <span>Captured: {new Date(question.llm.captured_at).toLocaleDateString()}</span>
        <span className="flex items-center gap-1.5">
          <Clock className="h-3.5 w-3.5" aria-hidden="true" />
          {question.llm.wall_clock_ms} ms · {question.llm.tokens} tokens
        </span>
      </div>
      <p className="mt-3 text-xs leading-5 text-text-secondary">
        Labelled fixture: identical question text, no structured retrieval, no graph trace.
      </p>
    </section>
  );
}
