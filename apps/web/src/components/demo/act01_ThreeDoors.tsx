"use client";

import { ArrowRight } from "lucide-react";
import { DOORS, type DemoDoor } from "./data/doors";

export function Act01ThreeDoors({ onPick }: { onPick: (door: DemoDoor) => void }) {
  return (
    <div className="grid h-full min-h-[520px] content-center gap-4 xl:grid-cols-3">
      {DOORS.map((door) => (
        <button
          key={door.id}
          onClick={() => onPick(door)}
          className="group rounded-lg border border-border bg-background p-5 text-left transition hover:border-accent/60 hover:bg-surface-hover"
        >
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">{door.domain}</p>
          <h2 className="mt-3 text-2xl font-semibold text-text-primary">{door.title}</h2>
          <p className="mt-2 text-sm text-text-secondary">{door.subtitle}</p>
          <blockquote className="mt-5 border-l-2 border-accent pl-3 text-sm italic leading-6 text-text-primary">
            {door.pitchQuestion}
          </blockquote>
          <p className="mt-4 text-xs leading-5 text-text-secondary">{door.pitchSubtext}</p>
          <div className="mt-5 flex items-center justify-between text-xs text-text-secondary">
            <span>{door.sourceTitle}</span>
            <ArrowRight size={16} className="text-accent transition group-hover:translate-x-1" />
          </div>
        </button>
      ))}
    </div>
  );
}
