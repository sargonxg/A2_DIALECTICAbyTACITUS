import { Binary, BrainCircuit, Sigma } from "lucide-react";

interface Props {
  score: number;
}

export function DeterminismBadge({ score }: Props) {
  const mode =
    score >= 0.9 ? "pure-symbolic" : score >= 0.72 ? "hybrid trace" : "neural-augmented";
  const Icon = score >= 0.9 ? Sigma : score >= 0.72 ? Binary : BrainCircuit;
  const tone =
    score >= 0.9
      ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
      : score >= 0.72
        ? "border-cyan-500/40 bg-cyan-500/10 text-cyan-200"
        : "border-amber-500/40 bg-amber-500/10 text-amber-200";

  return (
    <span
      data-test="determinism-badge"
      className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold ${tone}`}
      title={`Determinism score: ${Math.round(score * 100)}%`}
    >
      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
      {mode} · {Math.round(score * 100)}%
    </span>
  );
}
