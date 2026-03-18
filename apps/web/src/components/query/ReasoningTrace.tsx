"use client";

import { useState } from "react";
import type { ReasoningStep } from "@/types/analysis";
import { ChevronDown, ChevronRight, Database, Brain, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  steps: ReasoningStep[];
}

const ICONS: Record<string, React.ElementType> = {
  retrieval: Database,
  symbolic: Cpu,
  generation: Brain,
};

export default function ReasoningTrace({ steps }: Props) {
  const [expanded, setExpanded] = useState(false);
  const totalMs = steps.reduce((sum, s) => sum + s.duration_ms, 0);

  return (
    <div className="card">
      <button onClick={() => setExpanded(!expanded)} className="flex items-center gap-2 w-full text-left">
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">
          Reasoning Trace ({steps.length} steps, {totalMs}ms)
        </span>
      </button>

      {expanded && (
        <div className="mt-3 space-y-2">
          {steps.map((step, i) => {
            const Icon = ICONS[step.type] || Brain;
            return (
              <div key={i} className="flex items-start gap-3 text-sm">
                <Icon size={14} className={cn(
                  step.type === "retrieval" ? "text-accent" : step.type === "symbolic" ? "text-warning" : "text-node-narrative",
                )} />
                <div className="flex-1">
                  <p className="text-text-primary">{step.description}</p>
                  {step.detail && <p className="text-xs text-text-secondary mt-0.5">{step.detail}</p>}
                </div>
                <span className="text-xs text-text-secondary font-mono">{step.duration_ms}ms</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
