"use client";

export function Act09EmbeddingProjection({ nodes }: { nodes: number }) {
  const count = Math.max(nodes, 18);
  return (
    <div className="relative h-[520px] overflow-hidden rounded-lg border border-border bg-background">
      {Array.from({ length: Math.min(count, 64) }).map((_, index) => (
        <span
          key={index}
          className="absolute h-3 w-3 rounded-full bg-accent"
          style={{
            left: `${8 + ((index * 37) % 84)}%`,
            top: `${10 + ((index * 23) % 78)}%`,
            opacity: 0.45 + ((index * 11) % 45) / 100,
          }}
        />
      ))}
      <div className="absolute bottom-4 left-4 rounded-lg border border-border bg-surface px-3 py-2 text-xs text-text-secondary">
        2D projection placeholder driven by compute_embeddings counts.
      </div>
    </div>
  );
}
