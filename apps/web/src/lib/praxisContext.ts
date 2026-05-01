import type { GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { deriveGraphOpsReviewQueue, type GraphOpsReviewItem } from "@/lib/graphopsReview";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

export type PraxisContextBundle = {
  kind: "tacitus.dialectica.praxis_context.v1";
  generatedAt: string;
  workspaceId: string;
  caseId: string;
  extractionRunId?: string;
  objective: string;
  readiness: {
    status: "ready" | "review" | "blocked";
    score: number;
    blockers: number;
    warnings: number;
    reviewItems: number;
    summary: string;
  };
  context: {
    actors: Array<{ id: string; name: string; type: string; confidence: number; evidenceId?: string }>;
    commitments: Array<{ id: string; actorId?: string; description: string; status: string; evidenceId?: string }>;
    constraints: Array<{ id: string; actorId?: string; description: string; type: string; evidenceId?: string }>;
    events: Array<{ id: string; description: string; episodeId?: string; confidence: number; evidenceId?: string }>;
    narratives: Array<{ id: string; actorId?: string; content: string; type: string; evidenceId?: string }>;
    claims: Array<{ id: string; text: string; status: string; actorId?: string; evidenceId?: string }>;
    topEvidence: Array<{ id: string; text: string; confidence: number }>;
  };
  answerConstraints: string[];
  nextQuestions: string[];
  reviewQueue: GraphOpsReviewItem[];
  benchmark?: {
    benchmarkId: string;
    overall: number;
    scores: GraphOpsBenchmarkResult["scores"];
  };
  counts: Record<string, number>;
};

function byType(primitives: GraphOpsPrimitive[], type: string) {
  return primitives.filter((primitive) => primitive.primitive_type === type);
}

function primitiveText(primitive: GraphOpsPrimitive) {
  return String(
    primitive.provenance_span ??
      primitive.text ??
      primitive.description ??
      primitive.content ??
      primitive.name ??
      primitive.title ??
      "",
  );
}

function evidenceId(primitive: GraphOpsPrimitive) {
  return typeof primitive.evidence_span_id === "string" ? primitive.evidence_span_id : undefined;
}

function countTypes(primitives: GraphOpsPrimitive[]) {
  return primitives.reduce<Record<string, number>>((acc, primitive) => {
    acc[primitive.primitive_type] = (acc[primitive.primitive_type] ?? 0) + 1;
    return acc;
  }, {});
}

function readinessFrom(input: {
  benchmark?: GraphOpsBenchmarkResult;
  ruleEvaluation?: RuleEvaluationResult;
  reviewQueue: GraphOpsReviewItem[];
  counts: Record<string, number>;
}) {
  const blockers =
    input.reviewQueue.filter((item) => item.severity === "blocker").length +
    (input.ruleEvaluation?.summary.blocker ?? 0);
  const warnings =
    input.reviewQueue.filter((item) => item.severity === "warning").length +
    (input.ruleEvaluation?.summary.warning ?? 0);
  const baseScore = input.benchmark?.scores.overall ?? 0.55;
  const ontologyPenalty = ["Actor", "Claim", "EvidenceSpan"].filter((type) => !input.counts[type]).length * 0.15;
  const score = Math.max(0, Math.min(1, Math.round((baseScore - blockers * 0.2 - warnings * 0.04 - ontologyPenalty) * 100) / 100));
  const status = blockers > 0 || score < 0.45 ? "blocked" : warnings > 0 || score < 0.75 ? "review" : "ready";
  return {
    status,
    score,
    blockers,
    warnings,
    reviewItems: input.reviewQueue.length,
    summary:
      status === "ready"
        ? "The context is strong enough for a first Praxis graph-grounded answer with citations."
        : status === "review"
          ? "Praxis can use this as draft context, but should surface uncertainty and review prompts."
          : "Do not use this for final Praxis generation until blockers are resolved.",
  } as const;
}

export function buildPraxisContextBundle(input: {
  workspaceId: string;
  caseId: string;
  extractionRunId?: string;
  objective: string;
  primitives: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
  benchmark?: GraphOpsBenchmarkResult;
  nextQuestions?: string[];
}): PraxisContextBundle {
  const counts = countTypes(input.primitives);
  const reviewQueue = deriveGraphOpsReviewQueue({
    primitives: input.primitives,
    ruleEvaluation: input.ruleEvaluation,
    benchmark: input.benchmark,
  });
  const readiness = readinessFrom({
    benchmark: input.benchmark,
    ruleEvaluation: input.ruleEvaluation,
    reviewQueue,
    counts,
  });

  return {
    kind: "tacitus.dialectica.praxis_context.v1",
    generatedAt: new Date().toISOString(),
    workspaceId: input.workspaceId,
    caseId: input.caseId,
    extractionRunId: input.extractionRunId,
    objective: input.objective,
    readiness,
    context: {
      actors: byType(input.primitives, "Actor")
        .slice(0, 40)
        .map((actor) => ({
          id: actor.id,
          name: String(actor.name ?? "Unknown actor"),
          type: String(actor.actor_type ?? "unknown"),
          confidence: actor.confidence,
          evidenceId: evidenceId(actor),
        })),
      commitments: byType(input.primitives, "Commitment")
        .slice(0, 30)
        .map((commitment) => ({
          id: commitment.id,
          actorId: typeof commitment.actor_id === "string" ? commitment.actor_id : undefined,
          description: String(commitment.description ?? primitiveText(commitment)),
          status: String(commitment.commitment_status ?? "candidate"),
          evidenceId: evidenceId(commitment),
        })),
      constraints: byType(input.primitives, "Constraint")
        .slice(0, 30)
        .map((constraint) => ({
          id: constraint.id,
          actorId: typeof constraint.actor_id === "string" ? constraint.actor_id : undefined,
          description: String(constraint.description ?? primitiveText(constraint)),
          type: String(constraint.constraint_type ?? "unknown"),
          evidenceId: evidenceId(constraint),
        })),
      events: byType(input.primitives, "Event")
        .slice(0, 40)
        .map((event) => ({
          id: event.id,
          description: String(event.description ?? primitiveText(event)),
          episodeId: typeof event.episode_id === "string" ? event.episode_id : undefined,
          confidence: event.confidence,
          evidenceId: evidenceId(event),
        })),
      narratives: byType(input.primitives, "Narrative")
        .slice(0, 30)
        .map((narrative) => ({
          id: narrative.id,
          actorId: typeof narrative.actor_id === "string" ? narrative.actor_id : undefined,
          content: String(narrative.content ?? primitiveText(narrative)),
          type: String(narrative.narrative_type ?? "unknown"),
          evidenceId: evidenceId(narrative),
        })),
      claims: byType(input.primitives, "Claim")
        .slice(0, 50)
        .map((claim) => ({
          id: claim.id,
          text: String(claim.text ?? primitiveText(claim)),
          status: String(claim.claim_status ?? "extracted"),
          actorId: typeof claim.subject_actor_id === "string" ? claim.subject_actor_id : undefined,
          evidenceId: evidenceId(claim),
        })),
      topEvidence: byType(input.primitives, "EvidenceSpan")
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 12)
        .map((span) => ({
          id: span.id,
          text: primitiveText(span).slice(0, 320),
          confidence: span.confidence,
        })),
    },
    answerConstraints: input.ruleEvaluation?.answerConstraints ?? [
      "Cite source evidence for every factual claim.",
      "Separate explicit source claims from inference.",
      "Ask for missing evidence instead of filling gaps.",
    ],
    nextQuestions: input.nextQuestions?.length
      ? input.nextQuestions
      : [
          "Which claims are explicit versus inferred?",
          "Which constraints block or shape available options?",
          "What source spans should a human review first?",
        ],
    reviewQueue,
    benchmark: input.benchmark
      ? {
          benchmarkId: input.benchmark.benchmarkId,
          overall: input.benchmark.scores.overall,
          scores: input.benchmark.scores,
        }
      : undefined,
    counts,
  };
}
