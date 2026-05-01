import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

export type GraphOpsBenchmarkScores = {
  ontologyCoverage: number;
  evidenceGrounding: number;
  sourceGrounding: number;
  causalDiscipline: number;
  ruleCompliance: number;
  answerUsefulness: number;
  overall: number;
};

export type GraphOpsBenchmarkResult = {
  benchmarkId: string;
  mode: "deterministic_graphops_benchmark";
  workspaceId: string;
  caseId: string;
  extractionRunId?: string;
  objective: string;
  question: string;
  createdAt: string;
  scores: GraphOpsBenchmarkScores;
  rubric: Array<{ metric: keyof GraphOpsBenchmarkScores; weight: number; rationale: string }>;
  diagnostics: {
    primitiveCounts: Record<string, number>;
    missingPrimitiveTypes: string[];
    weakEvidenceIds: string[];
    unsupportedCausalClaims: string[];
    topEvidenceSpans: Array<{ id: string; text: string; confidence: number }>;
    ruleSummary?: RuleEvaluationResult["summary"];
    benchmarkTargets: string[];
    recommendations: string[];
  };
};

export type GraphOpsBenchmarkInput = {
  workspaceId: string;
  caseId: string;
  extractionRunId?: string;
  objective: string;
  question: string;
  answer?: string;
  goldAnswer?: string;
  expectedPrimitiveTypes?: string[];
  primitives: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
};

const DEFAULT_EXPECTED_TYPES = [
  "Actor",
  "Claim",
  "Event",
  "Constraint",
  "EvidenceSpan",
  "Episode",
];

const STOPWORDS = new Set([
  "about",
  "after",
  "against",
  "because",
  "before",
  "being",
  "between",
  "could",
  "their",
  "there",
  "these",
  "those",
  "which",
  "while",
  "would",
  "under",
  "where",
  "what",
  "when",
  "with",
  "from",
  "that",
  "this",
  "they",
  "will",
]);

function clamp(value: number) {
  return Math.max(0, Math.min(1, Math.round(value * 100) / 100));
}

function tokens(text: string) {
  return [...text.toLowerCase().matchAll(/[a-z][a-z0-9-]{2,}/g)]
    .map((match) => match[0])
    .filter((token) => !STOPWORDS.has(token));
}

function overlapScore(left: string, right: string) {
  const leftTokens = new Set(tokens(left));
  const rightTokens = new Set(tokens(right));
  if (leftTokens.size === 0 || rightTokens.size === 0) return 0;
  let overlap = 0;
  for (const token of leftTokens) {
    if (rightTokens.has(token)) overlap += 1;
  }
  return clamp(overlap / Math.min(leftTokens.size, rightTokens.size));
}

function textOf(primitive: GraphOpsPrimitive) {
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

function countTypes(primitives: GraphOpsPrimitive[]) {
  return primitives.reduce<Record<string, number>>((acc, primitive) => {
    acc[primitive.primitive_type] = (acc[primitive.primitive_type] ?? 0) + 1;
    return acc;
  }, {});
}

function hasCausalEvidence(primitives: GraphOpsPrimitive[]) {
  return primitives.some((primitive) => /\bbecause|caused|therefore|led to|resulted in|as a result\b/i.test(textOf(primitive)));
}

function sourceGroundingScore(answer: string, primitives: GraphOpsPrimitive[]) {
  const evidence = primitives.filter((primitive) => primitive.primitive_type === "EvidenceSpan");
  if (!answer.trim()) return evidence.length > 0 ? 0.55 : 0.25;
  const top = evidence.slice(0, 12);
  if (top.length === 0) return 0.2;
  const best = Math.max(...top.map((primitive) => overlapScore(answer, textOf(primitive))));
  const cited = /\b(evidence|span|source|quote|according|reported|claims|says)\b/i.test(answer) ? 0.15 : 0;
  return clamp(best + cited);
}

function answerUsefulnessScore(input: GraphOpsBenchmarkInput) {
  const answer = input.answer?.trim() ?? "";
  if (input.goldAnswer?.trim()) return overlapScore(answer, input.goldAnswer);
  if (!answer) {
    const types = new Set(input.primitives.map((primitive) => primitive.primitive_type));
    return clamp((types.has("Actor") ? 0.2 : 0) + (types.has("Claim") ? 0.2 : 0) + (types.has("Constraint") ? 0.2 : 0) + (types.has("Event") ? 0.2 : 0));
  }
  const mentionsActors = input.primitives
    .filter((primitive) => primitive.primitive_type === "Actor")
    .some((primitive) => String(primitive.name ?? "").length > 2 && answer.toLowerCase().includes(String(primitive.name).toLowerCase()));
  const mentionsConstraints = /\bconstraint|deadline|cannot|must|law|rule|limit|penalty|risk\b/i.test(answer);
  const asksOrQualifies = /\bverify|uncertain|candidate|review|source|question|evidence\b/i.test(answer);
  return clamp((answer.length > 120 ? 0.35 : 0.15) + (mentionsActors ? 0.25 : 0) + (mentionsConstraints ? 0.2 : 0) + (asksOrQualifies ? 0.2 : 0));
}

export function runGraphOpsBenchmark(input: GraphOpsBenchmarkInput): GraphOpsBenchmarkResult {
  const primitiveCounts = countTypes(input.primitives);
  const expected = input.expectedPrimitiveTypes?.length ? input.expectedPrimitiveTypes : DEFAULT_EXPECTED_TYPES;
  const present = new Set(input.primitives.map((primitive) => primitive.primitive_type));
  const missingPrimitiveTypes = expected.filter((type) => !present.has(type));
  const claimLike = input.primitives.filter((primitive) =>
    ["Claim", "Event", "Constraint", "Commitment", "Narrative", "ActorState"].includes(primitive.primitive_type),
  );
  const groundedClaimLike = claimLike.filter((primitive) => primitive.evidence_span_id || primitive.provenance_span);
  const weakEvidenceIds = input.primitives
    .filter((primitive) => primitive.primitive_type === "EvidenceSpan" && primitive.confidence < 0.7)
    .map((primitive) => primitive.id);
  const answer = input.answer ?? "";
  const answerMakesCausalClaim = /\bbecause|caused|therefore|led to|resulted in|as a result\b/i.test(answer);
  const unsupportedCausalClaims = answerMakesCausalClaim && !hasCausalEvidence(input.primitives) ? [answer.slice(0, 220)] : [];
  const ruleSummary = input.ruleEvaluation?.summary;
  const rulePenalty =
    (ruleSummary?.blocker ?? 0) * 0.3 +
    (ruleSummary?.warning ?? 0) * 0.12 +
    (ruleSummary?.review ?? 0) * 0.05;

  const scores = {
    ontologyCoverage: clamp((expected.length - missingPrimitiveTypes.length) / expected.length),
    evidenceGrounding: clamp(groundedClaimLike.length / Math.max(claimLike.length, 1) - weakEvidenceIds.length * 0.03),
    sourceGrounding: sourceGroundingScore(answer, input.primitives),
    causalDiscipline: clamp(unsupportedCausalClaims.length > 0 ? 0.35 : answerMakesCausalClaim ? 0.75 : 1),
    ruleCompliance: clamp(1 - rulePenalty),
    answerUsefulness: answerUsefulnessScore(input),
    overall: 0,
  };

  const weights: Array<{ metric: keyof GraphOpsBenchmarkScores; weight: number; rationale: string }> = [
    { metric: "ontologyCoverage", weight: 0.18, rationale: "The extraction must cover the ontology needed for conflict, policy, and diplomacy questions." },
    { metric: "evidenceGrounding", weight: 0.22, rationale: "Claims, events, commitments, and constraints need source spans before they can support Praxis answers." },
    { metric: "sourceGrounding", weight: 0.16, rationale: "Generated answers should overlap with retrieved evidence rather than free-form summary." },
    { metric: "causalDiscipline", weight: 0.14, rationale: "The engine must separate chronology from causal attribution." },
    { metric: "ruleCompliance", weight: 0.16, rationale: "Neurosymbolic blockers and warnings should reduce readiness until handled." },
    { metric: "answerUsefulness", weight: 0.14, rationale: "The output should name actors, constraints, uncertainty, and useful next questions." },
  ];
  scores.overall = clamp(weights.reduce((sum, item) => sum + scores[item.metric] * item.weight, 0));

  const topEvidenceSpans = input.primitives
    .filter((primitive) => primitive.primitive_type === "EvidenceSpan")
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 5)
    .map((primitive) => ({
      id: primitive.id,
      text: textOf(primitive).slice(0, 260),
      confidence: primitive.confidence,
    }));

  const recommendations: string[] = [];
  if (missingPrimitiveTypes.length > 0) recommendations.push(`Run targeted extraction for: ${missingPrimitiveTypes.join(", ")}.`);
  if (scores.evidenceGrounding < 0.85) recommendations.push("Review primitives without direct evidence spans before graph-grounded answer generation.");
  if (unsupportedCausalClaims.length > 0) recommendations.push("Remove causal language or add explicit causal evidence before publishing the answer.");
  if ((ruleSummary?.blocker ?? 0) > 0) recommendations.push("Resolve blocker rule signals before benchmarking against Praxis production tasks.");
  if (scores.overall >= 0.8) recommendations.push("Ready for a Databricks judge pass against baseline and graph-grounded prompts.");

  return {
    benchmarkId: `bench_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`,
    mode: "deterministic_graphops_benchmark",
    workspaceId: input.workspaceId,
    caseId: input.caseId,
    extractionRunId: input.extractionRunId,
    objective: input.objective,
    question: input.question,
    createdAt: new Date().toISOString(),
    scores,
    rubric: weights,
    diagnostics: {
      primitiveCounts,
      missingPrimitiveTypes,
      weakEvidenceIds,
      unsupportedCausalClaims,
      topEvidenceSpans,
      ruleSummary,
      benchmarkTargets: input.ruleEvaluation?.benchmarkTargets ?? [],
      recommendations,
    },
  };
}
