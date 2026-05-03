"use client";

import { EntityBubble } from "./primitives/EntityBubble";

export function Act05GeminiExtraction({ rawEntities }: { rawEntities: number }) {
  const count = Math.max(rawEntities, 12);
  return (
    <div className="rounded-lg border border-border bg-background p-6">
      <p className="text-sm text-text-secondary">Raw candidate entities: {rawEntities}</p>
      <div className="mt-8 flex min-h-[360px] flex-wrap content-center items-center justify-center gap-6">
        {Array.from({ length: Math.min(count, 28) }).map((_, index) => (
          <EntityBubble
            key={index}
            label={["Actor", "Event", "Issue", "Norm"][index % 4]}
            type="candidate"
            confidence={0.45 + ((index * 17) % 50) / 100}
          />
        ))}
      </div>
    </div>
  );
}
