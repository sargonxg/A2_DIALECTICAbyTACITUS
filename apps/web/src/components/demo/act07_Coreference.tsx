"use client";

export function Act07Coreference({ mergedPairs }: { mergedPairs: number }) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-border bg-background p-6">
        <p className="text-xs uppercase tracking-wide text-text-secondary">Merged alias pairs</p>
        <p className="mt-3 text-5xl font-semibold text-text-primary">{mergedPairs}</p>
      </div>
      {["Romeo Montague <- Romeo, young Montague", "Assad regime <- Damascus government, regime forces", "Napoleon <- Bonaparte, Emperor"].map((line) => (
        <div key={line} className="rounded-lg border border-border bg-background p-4 text-sm text-text-secondary">
          {line}
        </div>
      ))}
    </div>
  );
}
