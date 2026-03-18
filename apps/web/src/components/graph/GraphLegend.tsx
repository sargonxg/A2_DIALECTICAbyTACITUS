"use client";

import { NODE_COLORS, GLASL_COLORS } from "@/lib/utils";

export default function GraphLegend() {
  return (
    <div className="card space-y-3 text-xs">
      <p className="font-semibold text-text-secondary uppercase tracking-wider">Legend</p>
      <div>
        <p className="text-text-secondary mb-1">Node Types</p>
        <div className="grid grid-cols-2 gap-1">
          {Object.entries(NODE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-text-secondary capitalize">{type.replace("_", " ")}</span>
            </div>
          ))}
        </div>
      </div>
      <div>
        <p className="text-text-secondary mb-1">Glasl Escalation</p>
        <div className="flex gap-1 h-2 rounded-full overflow-hidden">
          <div className="flex-1" style={{ backgroundColor: GLASL_COLORS["win-win"] }} title="Stages 1-3: Win-Win" />
          <div className="flex-1" style={{ backgroundColor: GLASL_COLORS["win-lose"] }} title="Stages 4-6: Win-Lose" />
          <div className="flex-1" style={{ backgroundColor: GLASL_COLORS["lose-lose"] }} title="Stages 7-9: Lose-Lose" />
        </div>
        <div className="flex justify-between text-text-secondary mt-0.5">
          <span>Win-Win</span>
          <span>Win-Lose</span>
          <span>Lose-Lose</span>
        </div>
      </div>
    </div>
  );
}
