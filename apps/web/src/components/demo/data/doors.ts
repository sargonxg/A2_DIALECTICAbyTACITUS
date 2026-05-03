export type DemoScenarioId = "romeo" | "war_peace" | "syria";

export interface DemoDoor {
  id: DemoScenarioId;
  title: string;
  subtitle: string;
  domain: string;
  pitchQuestion: string;
  pitchSubtext: string;
  sourceTitle: string;
  ingestKind: "gutenberg" | "text";
  ingestParams:
    | { book_id: string; title: string; tier: "lite" | "standard" | "full"; max_chars: number }
    | { text_path: string; tier: "lite" | "standard" | "full" };
  workspaceId: string;
  expectedCounts: { actors: number; events: number; issues: number; conflicts: number; edges: number };
  replayPath: string;
  handoffQuestionsCount: number;
}

export const DOORS: DemoDoor[] = [
  {
    id: "romeo",
    title: "Romeo and Juliet",
    subtitle: "Verona, ~1597 — interpersonal escalation cascade",
    domain: "Human friction",
    pitchQuestion:
      "When does this conflict cross from Glasl stage 6 into stage 9?",
    pitchSubtext:
      "ChatGPT can summarize the tragedy. DIALECTICA computes the event chain and shows the CAUSED edges.",
    sourceTitle: "Project Gutenberg #1513 — Shakespeare",
    ingestKind: "gutenberg",
    ingestParams: { book_id: "1513", title: "Romeo and Juliet", tier: "standard", max_chars: 60000 },
    workspaceId: "demo-romeo",
    expectedCounts: { actors: 9, events: 7, issues: 2, conflicts: 1, edges: 28 },
    replayPath: "/demo/replays/romeo.ndjson",
    handoffQuestionsCount: 8,
  },
  {
    id: "war_peace",
    title: "War and Peace",
    subtitle: "Russia, 1805-1812 — Napoleonic invasion, civilian impact",
    domain: "Armed conflict",
    pitchQuestion:
      "Is Napoleon's choice to advance after Borodino a free decision or a forced one?",
    pitchSubtext:
      "Tolstoy posed the question across 1,225 pages. DIALECTICA turns it into a graph problem.",
    sourceTitle: "Project Gutenberg #2600 — Tolstoy",
    ingestKind: "gutenberg",
    ingestParams: { book_id: "2600", title: "War and Peace", tier: "lite", max_chars: 80000 },
    workspaceId: "demo-war-peace",
    expectedCounts: { actors: 11, events: 9, issues: 2, conflicts: 2, edges: 33 },
    replayPath: "/demo/replays/war_peace.ndjson",
    handoffQuestionsCount: 7,
  },
  {
    id: "syria",
    title: "Syria 2011-2024",
    subtitle: "Multi-party armed conflict, external intervention, regime collapse",
    domain: "Armed conflict",
    pitchQuestion:
      "Did Russia's September 2015 intervention cause regime survival?",
    pitchSubtext:
      "An LLM gives a confident paragraph. DIALECTICA gives a counterfactual over intervention edges.",
    sourceTitle: "TACITUS curated briefing",
    ingestKind: "text",
    ingestParams: { text_path: "/demo/corpora/syria_2011_2024_briefing.txt", tier: "full" },
    workspaceId: "demo-syria",
    expectedCounts: { actors: 22, events: 14, issues: 5, conflicts: 1, edges: 70 },
    replayPath: "/demo/replays/syria.ndjson",
    handoffQuestionsCount: 8,
  },
];

export function getDoor(id: string): DemoDoor | undefined {
  return DOORS.find((door) => door.id === id);
}
