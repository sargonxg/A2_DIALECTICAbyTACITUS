"use client";

import { NODE_COLORS } from "@/lib/utils";

interface NarrativeFrame {
  id: string;
  actor: string;
  frame: string;
  type: string;
  strength: number;
}

interface Props {
  frames: NarrativeFrame[];
}

export default function NarrativeEcosystem({ frames }: Props) {
  const byActor = frames.reduce<Record<string, NarrativeFrame[]>>((acc, f) => {
    (acc[f.actor] = acc[f.actor] || []).push(f);
    return acc;
  }, {});

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Narrative Ecosystem</h3>
      <div className="space-y-4">
        {Object.entries(byActor).map(([actor, narratives]) => (
          <div key={actor}>
            <p className="text-sm font-medium text-text-primary mb-1">{actor}</p>
            <div className="space-y-1">
              {narratives.map((n) => (
                <div key={n.id} className="flex items-center gap-2">
                  <div className="h-2 rounded-full" style={{ width: `${n.strength * 100}%`, backgroundColor: NODE_COLORS.narrative, minWidth: "20px" }} />
                  <span className="text-xs text-text-secondary truncate">{n.frame}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
