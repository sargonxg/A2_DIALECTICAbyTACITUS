"use client";

export function ChunkBar({ total, active }: { total: number; active: number }) {
  const count = Math.max(total, 1);
  return (
    <div className="flex h-24 items-end gap-1 rounded-lg border border-border bg-background p-3">
      {Array.from({ length: Math.min(count, 48) }).map((_, index) => (
        <div
          key={index}
          className={`flex-1 rounded-t ${index < active ? "bg-accent" : "bg-surface-hover"}`}
          style={{ height: `${24 + ((index * 13) % 56)}%` }}
        />
      ))}
    </div>
  );
}
