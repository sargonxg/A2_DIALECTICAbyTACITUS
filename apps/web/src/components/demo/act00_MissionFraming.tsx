"use client";

export function Act00MissionFraming({ onShow }: { onShow: () => void }) {
  return (
    <div className="flex h-full min-h-[520px] flex-col justify-center">
      <p className="text-xs font-semibold uppercase tracking-wide text-accent">DIALECTICA ingestion theatre</p>
      <h2 className="mt-4 max-w-4xl text-4xl font-semibold leading-tight text-text-primary">
        A deterministic substrate for conflict starts before the first answer.
      </h2>
      <div className="mt-8 grid gap-3 md:grid-cols-3">
        {[
          "Every conflict has a structure.",
          "Conflict scholarship gives names to that structure.",
          "DIALECTICA makes the structure executable and auditable.",
        ].map((line) => (
          <div key={line} className="rounded-lg border border-border bg-background p-5 text-sm leading-6 text-text-secondary">
            {line}
          </div>
        ))}
      </div>
      <button className="btn-primary mt-8 w-fit" onClick={onShow}>
        Show me
      </button>
    </div>
  );
}
