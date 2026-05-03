"use client";

import type { PipelineEvent } from "./types";

export function EventLogDrawer({
  open,
  events,
  onClose,
}: {
  open: boolean;
  events: PipelineEvent[];
  onClose: () => void;
}) {
  if (!open) return null;
  return (
    <div className="fixed bottom-0 right-0 top-0 z-[80] w-full max-w-xl border-l border-border bg-background shadow-2xl">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-text-primary">Raw SSE Event Log</h2>
        <button className="btn-secondary" onClick={onClose}>
          Close
        </button>
      </div>
      <pre className="h-[calc(100vh-3.5rem)] overflow-auto p-4 text-xs leading-5 text-text-secondary">
        {JSON.stringify(events, null, 2)}
      </pre>
    </div>
  );
}
