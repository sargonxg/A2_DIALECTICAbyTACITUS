"use client";

import type { PipelineEvent, ReplayFrame } from "./types";

export async function loadReplay(path: string): Promise<ReplayFrame[]> {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Replay not found: ${path}`);
  const text = await response.text();
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line) as ReplayFrame);
}

export function playReplay(
  frames: ReplayFrame[],
  onEvent: (event: PipelineEvent) => void,
  speed = 0.08,
): () => void {
  const timers = frames.map((frame) =>
    window.setTimeout(() => onEvent(frame.data), Math.max(0, frame.t * speed)),
  );
  return () => timers.forEach((timer) => window.clearTimeout(timer));
}
