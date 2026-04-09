"use client";

import { useState, useCallback } from "react";
import {
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  Cpu,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { ReasoningTrace } from "@/types/api";

interface ReasoningPanelProps {
  traces: ReasoningTrace[];
  workspaceId: string;
  onValidate: (
    traceId: string,
    verdict: "confirmed" | "rejected",
    notes?: string,
  ) => Promise<void>;
}

interface TraceRowProps {
  trace: ReasoningTrace;
  onValidate: (
    traceId: string,
    verdict: "confirmed" | "rejected",
    notes?: string,
  ) => Promise<void>;
}

function ConfidenceBadge({
  type,
  score,
}: {
  type: "deterministic" | "probabilistic";
  score: number;
}) {
  const isDeterministic = type === "deterministic";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold",
        isDeterministic
          ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
          : "bg-amber-950 text-amber-300 border border-amber-800",
      )}
    >
      {isDeterministic ? (
        <Shield size={10} className="shrink-0" />
      ) : (
        <Cpu size={10} className="shrink-0" />
      )}
      {isDeterministic ? "deterministic" : "probabilistic"}
      <span className="opacity-70">{Math.round(score * 100)}%</span>
    </span>
  );
}

function ValidationStatus({ trace }: { trace: ReasoningTrace }) {
  if (!trace.human_validated) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] text-zinc-500">
        <Clock size={10} />
        pending review
      </span>
    );
  }
  const confirmed = trace.human_verdict === "confirmed";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-[10px]",
        confirmed ? "text-emerald-400" : "text-red-400",
      )}
    >
      {confirmed ? <CheckCircle2 size={10} /> : <XCircle size={10} />}
      {confirmed ? "confirmed" : "rejected"}
    </span>
  );
}

function TraceRow({ trace, onValidate }: TraceRowProps) {
  const [expanded, setExpanded] = useState(false);
  const [validating, setValidating] = useState(false);
  const [notes, setNotes] = useState("");
  const [showNotes, setShowNotes] = useState(false);
  const [localValidated, setLocalValidated] = useState(trace.human_validated);
  const [localVerdict, setLocalVerdict] = useState(trace.human_verdict);

  const handleValidate = useCallback(
    async (verdict: "confirmed" | "rejected") => {
      setValidating(true);
      try {
        await onValidate(trace.id, verdict, notes || undefined);
        setLocalValidated(true);
        setLocalVerdict(verdict);
        setShowNotes(false);
        setNotes("");
      } finally {
        setValidating(false);
      }
    },
    [onValidate, trace.id, notes],
  );

  return (
    <div className="border border-zinc-800 rounded-lg overflow-hidden">
      {/* Header row */}
      <button
        className="w-full flex items-start gap-3 p-3 text-left hover:bg-zinc-900/60 transition-colors"
        onClick={() => setExpanded((v) => !v)}
      >
        <span className="mt-0.5 text-zinc-600 shrink-0">
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>

        <div className="flex-1 min-w-0 space-y-1">
          <p className="text-sm text-zinc-100 leading-snug">{trace.conclusion}</p>
          <div className="flex flex-wrap items-center gap-2">
            <ConfidenceBadge type={trace.confidence_type} score={trace.confidence_score} />
            <ValidationStatus
              trace={{ ...trace, human_validated: localValidated, human_verdict: localVerdict }}
            />
            <span className="text-[10px] text-zinc-600">
              {trace.rules_fired.length} rule{trace.rules_fired.length !== 1 ? "s" : ""}
            </span>
          </div>
        </div>
      </button>

      {/* Expanded body */}
      {expanded && (
        <div className="border-t border-zinc-800 px-4 py-3 space-y-3 bg-zinc-950/40">
          {/* Rules fired */}
          {trace.rules_fired.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-1.5">
                Rules fired
              </p>
              <ul className="space-y-0.5">
                {trace.rules_fired.map((rule, i) => (
                  <li
                    key={i}
                    className="text-xs text-zinc-400 font-mono bg-zinc-900 rounded px-2 py-0.5"
                  >
                    {rule}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Source nodes */}
          {trace.source_node_ids.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-1.5">
                Source nodes
              </p>
              <div className="flex flex-wrap gap-1">
                {trace.source_node_ids.map((id) => (
                  <span
                    key={id}
                    className="text-[10px] font-mono text-zinc-400 bg-zinc-900 rounded px-1.5 py-0.5"
                  >
                    {id.slice(0, 16)}…
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Validation actions */}
          {!localValidated && (
            <div className="space-y-2">
              <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">
                Human validation
              </p>

              {showNotes && (
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Optional notes…"
                  rows={2}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded px-2 py-1.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500 resize-none"
                />
              )}

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleValidate("confirmed")}
                  disabled={validating}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-emerald-900/50 border border-emerald-800 text-emerald-300 text-xs hover:bg-emerald-900 transition-colors disabled:opacity-50"
                >
                  <CheckCircle2 size={12} />
                  Confirm
                </button>
                <button
                  onClick={() => handleValidate("rejected")}
                  disabled={validating}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-red-900/50 border border-red-800 text-red-300 text-xs hover:bg-red-900 transition-colors disabled:opacity-50"
                >
                  <XCircle size={12} />
                  Reject
                </button>
                <button
                  onClick={() => setShowNotes((v) => !v)}
                  className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                  {showNotes ? "Hide notes" : "+ Add notes"}
                </button>
              </div>
            </div>
          )}

          {localValidated && (
            <p className="text-[10px] text-zinc-600 italic">
              Validated by human reviewer
              {localVerdict ? ` — ${localVerdict}` : ""}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function ReasoningPanel({
  traces,
  workspaceId: _workspaceId,
  onValidate,
}: ReasoningPanelProps) {
  const [filter, setFilter] = useState<"all" | "pending" | "deterministic" | "probabilistic">(
    "all",
  );

  const filtered = traces.filter((t) => {
    if (filter === "pending") return !t.human_validated;
    if (filter === "deterministic") return t.confidence_type === "deterministic";
    if (filter === "probabilistic") return t.confidence_type === "probabilistic";
    return true;
  });

  const pendingCount = traces.filter((t) => !t.human_validated).length;

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <div className="flex items-center gap-4 text-xs text-zinc-500">
        <span>{traces.length} traces total</span>
        {pendingCount > 0 && (
          <span className="text-amber-400 font-medium">{pendingCount} awaiting validation</span>
        )}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1">
        {(["all", "pending", "deterministic", "probabilistic"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "px-3 py-1 rounded text-xs transition-colors capitalize",
              filter === f
                ? "bg-zinc-700 text-white"
                : "text-zinc-500 hover:text-zinc-300",
            )}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Trace list */}
      {filtered.length === 0 ? (
        <div className="text-center py-12 text-zinc-600 text-sm">
          No reasoning traces match this filter.
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((trace) => (
            <TraceRow key={trace.id} trace={trace} onValidate={onValidate} />
          ))}
        </div>
      )}
    </div>
  );
}
