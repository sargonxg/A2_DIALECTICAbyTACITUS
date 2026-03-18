"use client";

import { GLASL_COLORS, glaslLevel } from "@/lib/utils";
import { cn } from "@/lib/utils";

const STAGES = [
  { stage: 1, name: "Hardening" },
  { stage: 2, name: "Debate" },
  { stage: 3, name: "Actions" },
  { stage: 4, name: "Coalitions" },
  { stage: 5, name: "Loss of Face" },
  { stage: 6, name: "Threats" },
  { stage: 7, name: "Limited Strikes" },
  { stage: 8, name: "Fragmentation" },
  { stage: 9, name: "Together into Abyss" },
];

export default function GlaslStageIndicator({ currentStage }: { currentStage: number }) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Glasl Escalation Model</h3>
      <div className="flex gap-0.5">
        {STAGES.map(({ stage, name }) => {
          const level = glaslLevel(stage);
          const active = stage === currentStage;
          return (
            <div key={stage} className="flex-1 relative group">
              <div
                className={cn("h-8 rounded-sm transition-all", active ? "ring-2 ring-white/50 scale-y-110" : "")}
                style={{ backgroundColor: active ? GLASL_COLORS[level] : GLASL_COLORS[level] + "30" }}
              />
              <div className={cn("text-center mt-1", active ? "text-text-primary" : "text-text-secondary")}>
                <p className="text-[10px] font-mono">{stage}</p>
              </div>
              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block z-10">
                <div className="bg-surface border border-border rounded px-2 py-1 text-[10px] text-text-primary whitespace-nowrap shadow-lg">
                  {name}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
