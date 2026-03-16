"use client";

import { cn } from "@/lib/utils";
import type { KriesbergPhase } from "@/types/ontology";

const PHASES: { value: KriesbergPhase; label: string }[] = [
  { value: "emergence", label: "Emergence" },
  { value: "escalation", label: "Escalation" },
  { value: "de_escalation", label: "De-escalation" },
  { value: "settlement", label: "Settlement" },
  { value: "post_settlement", label: "Post-settlement" },
];

export default function KriesbergPhaseTracker({ currentPhase }: { currentPhase?: KriesbergPhase }) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Kriesberg Phase</h3>
      <div className="flex items-center gap-1">
        {PHASES.map((phase, i) => {
          const active = phase.value === currentPhase;
          return (
            <div key={phase.value} className="flex-1 text-center">
              <div className={cn(
                "h-2 rounded-full",
                active ? "bg-accent" : "bg-surface-hover",
              )} />
              <p className={cn("text-[10px] mt-1", active ? "text-accent font-medium" : "text-text-secondary")}>
                {phase.label}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
