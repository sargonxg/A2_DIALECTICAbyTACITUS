"use client";

import type { DemoDoor } from "./data/doors";

export function Act02SourceReveal({ door, sourceText }: { door: DemoDoor | null; sourceText: string }) {
  return (
    <div className="grid h-full min-h-[520px] gap-4 xl:grid-cols-[320px_1fr]">
      <aside className="rounded-lg border border-border bg-background p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-accent">Selected corpus</p>
        <h2 className="mt-3 text-2xl font-semibold text-text-primary">{door?.title ?? "No corpus selected"}</h2>
        <p className="mt-2 text-sm leading-6 text-text-secondary">{door?.sourceTitle}</p>
      </aside>
      <pre className="max-h-[640px] overflow-auto rounded-lg border border-border bg-background p-5 text-xs leading-6 text-text-secondary">
        {sourceText || "The first source preview appears here before extraction begins."}
      </pre>
    </div>
  );
}
