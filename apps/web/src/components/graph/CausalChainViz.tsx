"use client";

import type { CausalChain } from "@/types/analysis";

interface Props {
  chain: CausalChain;
  pearlLevel: "association" | "intervention" | "counterfactual";
  onPearlChange: (level: "association" | "intervention" | "counterfactual") => void;
}

const PEARL_LEVELS = ["association", "intervention", "counterfactual"] as const;

export default function CausalChainViz({ chain, pearlLevel, onPearlChange }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {PEARL_LEVELS.map((level) => (
          <button
            key={level}
            onClick={() => onPearlChange(level)}
            className={`badge ${pearlLevel === level ? "bg-accent/20 text-accent" : "bg-surface-hover text-text-secondary"}`}
          >
            {level}
          </button>
        ))}
      </div>

      <div className="relative">
        {chain.events.map((event, i) => (
          <div key={event.id} className="flex items-center gap-3 mb-4">
            <div className="w-3 h-3 rounded-full bg-warning flex-shrink-0" style={{ opacity: event.significance }} />
            <div className="flex-1 card">
              <p className="text-sm font-medium text-text-primary">{event.name}</p>
              {event.occurred_at && (
                <p className="text-xs text-text-secondary">{event.occurred_at}</p>
              )}
            </div>
            {i < chain.events.length - 1 && (
              <div className="absolute left-[5px] mt-3 w-0.5 h-4 bg-surface-active" style={{ top: `${i * 72 + 24}px` }} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
