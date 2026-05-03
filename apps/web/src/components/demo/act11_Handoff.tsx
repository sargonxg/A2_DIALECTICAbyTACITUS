"use client";

import Link from "next/link";
import type { DemoDoor } from "./data/doors";

export function Act11Handoff({ door, onReset }: { door: DemoDoor | null; onReset: () => void }) {
  return (
    <div className="flex h-full min-h-[520px] flex-col justify-center">
      <p className="text-xs font-semibold uppercase tracking-wide text-accent">Graph built</p>
      <h2 className="mt-4 max-w-3xl text-4xl font-semibold text-text-primary">
        Now you can ask things a plain LLM cannot answer with a trace.
      </h2>
      <blockquote className="mt-6 max-w-3xl border-l-2 border-accent pl-4 text-lg italic leading-8 text-text-secondary">
        {door?.pitchQuestion}
      </blockquote>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link href={`/demo/${door?.id ?? "romeo"}/reasoning`} className="btn-primary">
          Ask DIALECTICA
        </Link>
        <button className="btn-secondary" onClick={onReset}>
          Try a different scenario
        </button>
      </div>
    </div>
  );
}
