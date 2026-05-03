"use client";

export function Act08Relationships({ edges }: { edges: number }) {
  return (
    <div className="rounded-lg border border-border bg-background p-6">
      <p className="text-xs uppercase tracking-wide text-text-secondary">Validated relationships</p>
      <p className="mt-3 text-5xl font-semibold text-text-primary">{edges}</p>
      <div className="mt-8 grid gap-3 md:grid-cols-3">
        {["CAUSED", "OPPOSED_TO", "EVIDENCED_BY"].map((edge) => (
          <div key={edge} className="rounded-lg border border-accent/20 bg-accent/10 p-4 text-sm font-semibold text-accent">
            {edge}
          </div>
        ))}
      </div>
    </div>
  );
}
