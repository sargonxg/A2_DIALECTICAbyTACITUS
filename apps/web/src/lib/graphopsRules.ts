import { neurosymbolicRuleCatalog } from "@/data/graphops";
import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";

export type RuleSignal = {
  id: string;
  rule_id: string;
  rule_name: string;
  category: string;
  severity: "info" | "review" | "warning" | "blocker";
  status: "fired" | "not_fired";
  rationale: string;
  evidence_ids: string[];
  affected_ids: string[];
  recommended_action: string;
  benchmark_target: string;
};

export type RuleEvaluationResult = {
  mode: "deterministic_neurosymbolic_rules";
  summary: {
    fired: number;
    review: number;
    warning: number;
    blocker: number;
  };
  signals: RuleSignal[];
  answerConstraints: string[];
  benchmarkTargets: string[];
};

function signal(input: Omit<RuleSignal, "id" | "status">): RuleSignal {
  return {
    id: `signal_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`,
    status: "fired",
    ...input,
  };
}

function byType(primitives: GraphOpsPrimitive[], type: string) {
  return primitives.filter((item) => item.primitive_type === type);
}

function lowerText(item: GraphOpsPrimitive) {
  return String(item.provenance_span ?? item.text ?? item.description ?? item.content ?? "").toLowerCase();
}

function ruleMeta(ruleId: string) {
  return neurosymbolicRuleCatalog.find((rule) => rule.id === ruleId) ?? neurosymbolicRuleCatalog[0];
}

export function evaluateNeurosymbolicRules(primitives: GraphOpsPrimitive[]): RuleEvaluationResult {
  const signals: RuleSignal[] = [];
  const claims = byType(primitives, "Claim");
  const commitments = byType(primitives, "Commitment");
  const constraints = byType(primitives, "Constraint");
  const events = byType(primitives, "Event");
  const narratives = byType(primitives, "Narrative");
  const actorStates = byType(primitives, "ActorState");
  const evidence = byType(primitives, "EvidenceSpan");
  const actors = byType(primitives, "Actor");

  if (commitments.length > 0 && constraints.length > 0) {
    const rule = ruleMeta("commitment-constraint-propagation");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: "review",
        rationale: "The extraction contains both commitments and constraints. Answer generation must distinguish promised action from binding constraint and contested scope.",
        evidence_ids: commitments.flatMap((item) => item.evidence_span_id ? [item.evidence_span_id] : []).slice(0, 6),
        affected_ids: [...commitments, ...constraints].map((item) => item.id).slice(0, 10),
        recommended_action: "Create a commitment ledger and ask which commitments are explicit, ambiguous, denied, or constrained.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  if (events.length >= 2) {
    const causalWords = events.filter((event) => /\bbecause|caused|therefore|led to|resulted\b/i.test(lowerText(event)));
    const rule = ruleMeta("causal-vs-temporal-separation");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: causalWords.length > 0 ? "review" : "warning",
        rationale:
          causalWords.length > 0
            ? "Some event spans contain causal language, but causal edges still require evidence and confidence."
            : "Multiple events were extracted, but causality is not explicit. Do not let the LLM convert sequence into cause.",
        evidence_ids: events.flatMap((item) => item.evidence_span_id ? [item.evidence_span_id] : []).slice(0, 6),
        affected_ids: events.map((item) => item.id).slice(0, 10),
        recommended_action: "Represent chronology with PRECEDES and create CAUSED only when source evidence supports causal wording.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  if (actorStates.some((state) => state.leverage_level) || constraints.some((item) => /banish|penalt|authority|fund|deadline|must|cannot/i.test(lowerText(item)))) {
    const rule = ruleMeta("power-asymmetry-process-risk");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: "review",
        rationale: "The graph contains leverage or hard constraints. Direct negotiation or simple summary may hide asymmetric process risk.",
        evidence_ids: [...actorStates, ...constraints].flatMap((item) => item.evidence_span_id ? [item.evidence_span_id] : []).slice(0, 6),
        affected_ids: [...actorStates, ...constraints].map((item) => item.id).slice(0, 10),
        recommended_action: "Ask whether guarantees, shuttle mediation, sequencing, or safeguards are required before joint process.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  if (claims.some((claim) => claim.confidence < 0.7) || evidence.some((span) => span.confidence < 0.75)) {
    const rule = ruleMeta("source-trust-claim-downgrade");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: "review",
        rationale: "Some claims or evidence spans are below strong-confidence thresholds. They should remain candidate facts until reviewed or corroborated.",
        evidence_ids: evidence.filter((span) => span.confidence < 0.75).map((span) => span.id).slice(0, 8),
        affected_ids: claims.filter((claim) => claim.confidence < 0.7).map((claim) => claim.id).slice(0, 8),
        recommended_action: "Keep low-confidence claims out of final answer language unless clearly marked as unverified.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  const requiredForConflictBook = ["Actor", "Claim", "Event", "Narrative", "Constraint", "EvidenceSpan"];
  const present = new Set(primitives.map((item) => item.primitive_type));
  const missing = requiredForConflictBook.filter((type) => !present.has(type));
  if (missing.length > 0 || actors.length < 2) {
    const rule = ruleMeta("ontology-coverage-gate");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: missing.length > 1 ? "blocker" : "warning",
        rationale: `The conflict-resolution book lens expects actors, claims, events, narratives, constraints, and evidence. Missing or weak coverage: ${missing.join(", ") || "actor diversity"}.`,
        evidence_ids: evidence.map((item) => item.id).slice(0, 4),
        affected_ids: primitives.map((item) => item.id).slice(0, 8),
        recommended_action: "Run targeted extraction or add more source text before producing a final graph-grounded answer.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  if (constraints.length > 0 && actorStates.some((state) => state.trust_level) && commitments.length > 0) {
    const rule = ruleMeta("ripeness-signal");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: "info",
        rationale: "The graph contains commitments, constraints, and trust-state evidence. This is enough to ask whether a process or mediator intervention is viable.",
        evidence_ids: [...constraints, ...actorStates, ...commitments].flatMap((item) => item.evidence_span_id ? [item.evidence_span_id] : []).slice(0, 8),
        affected_ids: [...constraints, ...actorStates, ...commitments].map((item) => item.id).slice(0, 10),
        recommended_action: "Generate mediator verification questions before suggesting an intervention.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  if (narratives.some((item) => /\bhonor|love|hate|feud|betray|identity|legitimacy|humiliation\b/i.test(lowerText(item)))) {
    const rule = ruleMeta("narrative-identity-escalation");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: "warning",
        rationale: "Narrative evidence contains identity, loyalty, love, honor, feud, or betrayal language. Material-only analysis will be incomplete.",
        evidence_ids: narratives.flatMap((item) => item.evidence_span_id ? [item.evidence_span_id] : []).slice(0, 6),
        affected_ids: narratives.map((item) => item.id).slice(0, 8),
        recommended_action: "Add narrative de-escalation questions and avoid reducing the conflict to interests alone.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  if (constraints.some((item) => /\blaw|rule|only after|requires|must|cannot|deadline|expires\b/i.test(lowerText(item)))) {
    const rule = ruleMeta("legal-constraint-option-filter");
    signals.push(
      signal({
        rule_id: rule.id,
        rule_name: rule.name,
        category: rule.category,
        severity: "review",
        rationale: "Normative or procedural constraints were detected. Suggested options must be filtered against those constraints.",
        evidence_ids: constraints.flatMap((item) => item.evidence_span_id ? [item.evidence_span_id] : []).slice(0, 6),
        affected_ids: constraints.map((item) => item.id).slice(0, 8),
        recommended_action: "Attach governing constraint checks to answer plans and benchmark policy-constraint accuracy.",
        benchmark_target: rule.benchmark,
      }),
    );
  }

  const summary = {
    fired: signals.length,
    review: signals.filter((item) => item.severity === "review").length,
    warning: signals.filter((item) => item.severity === "warning").length,
    blocker: signals.filter((item) => item.severity === "blocker").length,
  };

  return {
    mode: "deterministic_neurosymbolic_rules",
    summary,
    signals,
    answerConstraints: [
      "Do not state causal claims unless a CAUSED edge or causal source span exists.",
      "Mark low-confidence claims as candidate or unverified.",
      "Prefer cited evidence spans over summary-only claims.",
      "Separate temporal order, commitments, constraints, leverage, and narrative frames.",
      "If ontology coverage is weak, ask for more sources or run targeted extraction before final answers.",
    ],
    benchmarkTargets: [...new Set(signals.map((item) => item.benchmark_target))],
  };
}
