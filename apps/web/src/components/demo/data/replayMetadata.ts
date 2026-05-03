import type { DemoScenarioId } from "./doors";

export const REPLAY_METADATA: Record<
  DemoScenarioId,
  { capturedAt: string; runId: string; source: string }
> = {
  romeo: {
    capturedAt: "2026-05-03T00:00:00Z",
    runId: "starter-replay-romeo",
    source: "Prompt 1 starter replay generated from canonical event shape",
  },
  war_peace: {
    capturedAt: "2026-05-03T00:00:00Z",
    runId: "starter-replay-war-peace",
    source: "Prompt 1 starter replay generated from canonical event shape",
  },
  syria: {
    capturedAt: "2026-05-03T00:00:00Z",
    runId: "starter-replay-syria",
    source: "Prompt 1 starter replay generated from canonical event shape",
  },
};
