"use client";

import type { PowerActor } from "@/types/analysis";
import { NODE_COLORS } from "@/lib/utils";

interface Props {
  actors: PowerActor[];
}

export default function PowerMap({ actors }: Props) {
  const sorted = [...actors].sort((a, b) => b.power_score - a.power_score);
  const max = sorted[0]?.power_score || 1;

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Power Distribution</h3>
      <div className="space-y-2">
        {sorted.map((actor) => (
          <div key={actor.id}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-text-primary">{actor.name}</span>
              <span className="font-mono text-xs text-text-secondary">{(actor.power_score * 100).toFixed(0)}</span>
            </div>
            <div className="h-4 bg-surface-hover rounded-full flex overflow-hidden">
              {Object.entries(actor.power_bases).map(([base, val]) => (
                <div
                  key={base}
                  className="h-full"
                  style={{ width: `${(val / max) * 100}%`, backgroundColor: NODE_COLORS.actor + "80" }}
                  title={`${base}: ${(val * 100).toFixed(0)}`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
