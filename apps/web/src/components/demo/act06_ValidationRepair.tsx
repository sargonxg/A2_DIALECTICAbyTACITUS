"use client";

export function Act06ValidationRepair({
  valid,
  invalid,
}: {
  valid: number;
  invalid: number;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Panel title="Schema-valid" value={valid} tone="text-emerald-200" />
      <Panel title="Rejected or repaired" value={invalid} tone="text-rose-200" />
      <div className="md:col-span-2 rounded-lg border border-border bg-background p-5 text-sm leading-6 text-text-secondary">
        Invalid objects never enter the graph silently. The repair loop is explicit, bounded, and visible in the event log.
      </div>
    </div>
  );
}

function Panel({ title, value, tone }: { title: string; value: number; tone: string }) {
  return (
    <div className="rounded-lg border border-border bg-background p-6">
      <p className="text-xs uppercase tracking-wide text-text-secondary">{title}</p>
      <p className={`mt-3 text-5xl font-semibold ${tone}`}>{value}</p>
    </div>
  );
}
