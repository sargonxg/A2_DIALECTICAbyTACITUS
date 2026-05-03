import { AlertTriangle, CheckCircle2, DatabaseZap, Loader2 } from "lucide-react";

interface Props {
  status: "fixture" | "loading" | "live" | "error";
}

export function LiveModeBadge({ status }: Props) {
  const config = {
    fixture: {
      label: "fixture mode",
      Icon: DatabaseZap,
      className: "border-slate-500/40 bg-slate-500/10 text-slate-200",
    },
    loading: {
      label: "running live",
      Icon: Loader2,
      className: "border-cyan-500/40 bg-cyan-500/10 text-cyan-200",
    },
    live: {
      label: "live API",
      Icon: CheckCircle2,
      className: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
    },
    error: {
      label: "fixture fallback",
      Icon: AlertTriangle,
      className: "border-amber-500/40 bg-amber-500/10 text-amber-200",
    },
  }[status];

  const Icon = config.Icon;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold ${config.className}`}>
      <Icon className={`h-3.5 w-3.5 ${status === "loading" ? "animate-spin" : ""}`} aria-hidden="true" />
      {config.label}
    </span>
  );
}
