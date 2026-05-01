import type { GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

export type GraphOpsReviewItem = {
  id: string;
  source: "rule" | "benchmark" | "primitive" | "entity_resolution" | "temporal";
  severity: "info" | "review" | "warning" | "blocker";
  category: string;
  title: string;
  rationale: string;
  evidenceIds: string[];
  primitiveIds: string[];
  recommendedAction: string;
};

const CLAIM_LIKE = new Set(["Claim", "Event", "Constraint", "Commitment", "Narrative", "ActorState"]);

function reviewId(prefix: string, seed: string) {
  return `${prefix}_${seed.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 80)}`;
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

function normalizeActorName(value: unknown) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

export function deriveGraphOpsReviewQueue(input: {
  primitives: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
  benchmark?: GraphOpsBenchmarkResult;
}): GraphOpsReviewItem[] {
  const items: GraphOpsReviewItem[] = [];

  for (const signal of input.ruleEvaluation?.signals ?? []) {
    if (signal.severity === "info") continue;
    items.push({
      id: reviewId("review_rule", signal.id),
      source: "rule",
      severity: signal.severity,
      category: signal.category,
      title: signal.rule_name,
      rationale: signal.rationale,
      evidenceIds: signal.evidence_ids,
      primitiveIds: signal.affected_ids,
      recommendedAction: signal.recommended_action,
    });
  }

  const weakEvidence = input.primitives.filter(
    (primitive) => primitive.primitive_type === "EvidenceSpan" && primitive.confidence < 0.7,
  );
  for (const primitive of weakEvidence.slice(0, 12)) {
    items.push({
      id: reviewId("review_weak_evidence", primitive.id),
      source: "primitive",
      severity: "review",
      category: "provenance",
      title: "Weak evidence span",
      rationale: `Evidence confidence is ${Math.round(primitive.confidence * 100)}% for: ${textOf(primitive).slice(0, 180)}`,
      evidenceIds: [primitive.id],
      primitiveIds: [primitive.id],
      recommendedAction: "Verify the source span or downgrade downstream answer language.",
    });
  }

  const ungrounded = input.primitives.filter(
    (primitive) => CLAIM_LIKE.has(primitive.primitive_type) && !primitive.evidence_span_id && !primitive.provenance_span,
  );
  for (const primitive of ungrounded.slice(0, 12)) {
    items.push({
      id: reviewId("review_ungrounded", primitive.id),
      source: "primitive",
      severity: "warning",
      category: "grounding",
      title: `${primitive.primitive_type} lacks direct provenance`,
      rationale: "A claim-like primitive should not support Praxis generation without an evidence span or provenance text.",
      evidenceIds: [],
      primitiveIds: [primitive.id],
      recommendedAction: "Attach evidence, rerun targeted extraction, or exclude this primitive from final answer context.",
    });
  }

  for (const missingType of input.benchmark?.diagnostics.missingPrimitiveTypes ?? []) {
    items.push({
      id: reviewId("review_missing_type", missingType),
      source: "benchmark",
      severity: "warning",
      category: "ontology_coverage",
      title: `Missing ${missingType}`,
      rationale: "The benchmark rubric expected this primitive type for the selected conflict/policy context.",
      evidenceIds: [],
      primitiveIds: [],
      recommendedAction: `Run targeted extraction or add source text that can support ${missingType} primitives.`,
    });
  }

  for (const unsupported of input.benchmark?.diagnostics.unsupportedCausalClaims ?? []) {
    items.push({
      id: reviewId("review_causal", unsupported),
      source: "benchmark",
      severity: "blocker",
      category: "causal_discipline",
      title: "Unsupported causal language",
      rationale: unsupported,
      evidenceIds: [],
      primitiveIds: [],
      recommendedAction: "Use temporal language or add explicit causal evidence before answer generation.",
    });
  }

  const actorsByName = new Map<string, GraphOpsPrimitive[]>();
  for (const actor of input.primitives.filter((primitive) => primitive.primitive_type === "Actor")) {
    const key = normalizeActorName(actor.name);
    if (!key) continue;
    actorsByName.set(key, [...(actorsByName.get(key) ?? []), actor]);
  }
  for (const [name, actors] of actorsByName) {
    if (actors.length < 2) continue;
    items.push({
      id: reviewId("review_actor_duplicate", name),
      source: "entity_resolution",
      severity: "review",
      category: "entity_resolution",
      title: `Possible duplicate actor: ${actors[0].name ?? name}`,
      rationale: `${actors.length} actor primitives share a normalized name and may need alias consolidation.`,
      evidenceIds: actors.flatMap((actor) => (actor.evidence_span_id ? [actor.evidence_span_id] : [])).slice(0, 8),
      primitiveIds: actors.map((actor) => actor.id),
      recommendedAction: "Confirm whether these mentions refer to one actor, aliases, or separate entities.",
    });
  }

  const undatedEvents = input.primitives.filter(
    (primitive) =>
      primitive.primitive_type === "Event" &&
      !primitive.valid_from &&
      !primitive.valid_to &&
      !primitive.occurred_at,
  );
  if (undatedEvents.length > 0) {
    items.push({
      id: "review_temporal_undated_events",
      source: "temporal",
      severity: "review",
      category: "temporal_reasoning",
      title: "Events need temporal normalization",
      rationale: `${undatedEvents.length} event primitive(s) do not carry valid_from, valid_to, or occurred_at fields.`,
      evidenceIds: undatedEvents.flatMap((event) => (event.evidence_span_id ? [event.evidence_span_id] : [])).slice(0, 8),
      primitiveIds: undatedEvents.map((event) => event.id).slice(0, 20),
      recommendedAction: "Infer explicit dates only when supported; otherwise preserve episode ordering and mark chronology as approximate.",
    });
  }

  return items.slice(0, 40);
}
