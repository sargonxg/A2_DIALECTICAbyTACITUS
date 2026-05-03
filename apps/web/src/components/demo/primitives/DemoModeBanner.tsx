"use client";

import type { DemoMode } from "./types";

export function DemoModeBanner({ mode, detail }: { mode: DemoMode; detail?: string }) {
  if (mode === "idle") return null;
  const live = mode === "live";
  return (
    <div
      className={`fixed left-1/2 top-3 z-[70] -translate-x-1/2 rounded-lg border px-3 py-2 text-xs shadow-lg ${
        live
          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-100"
          : "border-amber-500/30 bg-amber-500/10 text-amber-100"
      }`}
    >
      {live ? "Live mode — reading canonical SSE events." : "Replay mode — live API unavailable or skipped."}
      {detail ? ` ${detail}` : ""}
    </div>
  );
}
