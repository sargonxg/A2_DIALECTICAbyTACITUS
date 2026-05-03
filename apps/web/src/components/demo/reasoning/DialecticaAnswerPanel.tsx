import { CheckCircle2, Database, DollarSign, Timer } from "lucide-react";
import { DeterminismBadge } from "./DeterminismBadge";
import { HallucinationGauge } from "./HallucinationGauge";
import type { CuratedReasoningQuestion } from "./types";

interface Props {
  question: CuratedReasoningQuestion;
  counterfactualActive: boolean;
  onTraceOpen: () => void;
}

export function DialecticaAnswerPanel({ question, counterfactualActive, onTraceOpen }: Props) {
  const result = question.dialectica;

  return (
    <section data-test="dialectica-answer" className="rounded-lg border border-accent/35 bg-accent/5 p-4">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">DIALECTICA traced answer</p>
          <h3 className="mt-1 text-lg font-semibold text-text-primary">{result.primary_framework}</h3>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {counterfactualActive && (
            <span data-test="counterfactual-pill" className="rounded-md border border-amber-400/50 bg-amber-400/10 px-2.5 py-1 text-xs font-semibold text-amber-200">
              Counterfactual
            </span>
          )}
          <DeterminismBadge score={result.determinism_score} />
        </div>
      </div>
      <p className="text-base font-semibold leading-7 text-text-primary">{result.answer_summary}</p>
      <p className="mt-3 text-sm leading-6 text-text-secondary">{result.answer_full}</p>

      {counterfactualActive && question.counterfactual && (
        <div data-test="diff-glasl-stage" className="mt-4 rounded-md border border-amber-500/30 bg-amber-500/10 p-3">
          <p className="text-sm font-semibold text-amber-100">{question.counterfactual.result_summary}</p>
          <p className="mt-1 text-xs leading-5 text-amber-100/80">{question.counterfactual.diff}</p>
        </div>
      )}

      <div className="mt-5 grid gap-3 border-t border-border pt-4 md:grid-cols-2">
        <HallucinationGauge value={result.hallucination_risk} />
        <div className="grid grid-cols-3 gap-2 text-xs text-text-secondary">
          <span className="flex items-center gap-1.5">
            <Timer className="h-3.5 w-3.5" aria-hidden="true" />
            {result.elapsed_ms} ms
          </span>
          <span className="flex items-center gap-1.5">
            <DollarSign className="h-3.5 w-3.5" aria-hidden="true" />
            ${result.cost_usd.toFixed(4)}
          </span>
          <span className="flex items-center gap-1.5">
            <Database className="h-3.5 w-3.5" aria-hidden="true" />
            {result.cited_node_ids.length + result.cited_edge_ids.length} cites
          </span>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" onClick={onTraceOpen} className="btn-primary">
          Open trace
        </button>
        <span className="inline-flex items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs font-semibold text-emerald-200">
          <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
          Typed result object
        </span>
      </div>
    </section>
  );
}
