import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

export type RetrievalStrategy =
  | "vector"
  | "vector_cypher"
  | "hybrid"
  | "text2cypher"
  | "global_community"
  | "multi";

export type GraphOpsRetrievalPlan = {
  kind: "tacitus.dialectica.retrieval_plan.v1";
  question: string;
  strategy: RetrievalStrategy;
  primitiveFocus: string[];
  traversalDepth: number;
  topK: number;
  sourceBudgetChars: number;
  confidenceFloor: number;
  abstainIf: string[];
  requireProvenance: boolean;
  temporalWindow: { start: string | null; end: string | null } | null;
  routeRationale: string[];
  cypherTemplate: string;
  contextAssembly: string[];
  requiredIndexes: string[];
};

export type GraphOpsRetrievalContextItem = {
  id: string;
  primitiveType: string;
  label: string;
  confidence: number | null;
  text: string;
  evidenceIds: string[];
  neighborIds: string[];
  quoteIds: string[];
};

export type GraphOpsRetrievalExecution = {
  kind: "tacitus.dialectica.retrieval_execution.v1";
  executedAt: string;
  mode: "local_primitives" | "neo4j_cypher";
  plan: GraphOpsRetrievalPlan;
  answerPolicy: {
    mayAnswer: boolean;
    reasons: string[];
    requiredDisclosures: string[];
  };
  context: GraphOpsRetrievalContextItem[];
  citations: Array<{
    id: string;
    quote: string;
    sourceId: string | null;
    chunkId: string | null;
    supports: string[];
  }>;
  ruleFindings: Array<{
    ruleId: string;
    severity: string;
    rationale: string;
    affectedIds: string[];
  }>;
  executedCypher?: string;
  diagnostics: {
    contextItems: number;
    citations: number;
    lowConfidenceItems: number;
    blockerSignals: number;
    missingEvidenceItems: number;
  };
};

const PRIMITIVES = [
  "Actor",
  "Claim",
  "Interest",
  "Constraint",
  "Leverage",
  "Commitment",
  "Event",
  "Narrative",
];

function includesAny(text: string, words: string[]) {
  return words.some((word) => text.includes(word));
}

function inferPrimitiveFocus(question: string, primitives: GraphOpsPrimitive[]) {
  const lower = question.toLowerCase();
  const focus = new Set<string>();
  const hints: Array<[string, string[]]> = [
    ["Actor", ["who", "actor", "party", "institution", "state", "ministry", "office"]],
    ["Claim", ["claim", "assert", "argue", "say", "position", "contradiction"]],
    ["Interest", ["interest", "need", "incentive", "priority", "why"]],
    ["Constraint", ["constraint", "rule", "deadline", "cannot", "must", "law", "option"]],
    ["Leverage", ["leverage", "power", "sanction", "pressure", "capacity"]],
    ["Commitment", ["commitment", "promise", "agree", "pledge", "obligation"]],
    ["Event", ["when", "event", "timeline", "before", "after", "happen", "caused"]],
    ["Narrative", ["narrative", "frame", "story", "theme", "legitimacy", "identity"]],
  ];
  for (const [primitive, words] of hints) {
    if (includesAny(lower, words)) focus.add(primitive);
  }
  for (const primitive of PRIMITIVES) {
    if (primitives.some((item) => item.primitive_type === primitive)) focus.add(primitive);
  }
  return [...focus].slice(0, 6);
}

function primitiveText(primitive: GraphOpsPrimitive) {
  return String(
    primitive.text ??
      primitive.description ??
      primitive.content ??
      primitive.name ??
      primitive.title ??
      primitive.provenance_span ??
      "",
  );
}

function primitiveLabel(primitive: GraphOpsPrimitive) {
  return primitiveText(primitive).slice(0, 140) || primitive.primitive_type;
}

function tokenSet(text: string) {
  return new Set(
    [...text.toLowerCase().matchAll(/[a-z][a-z0-9-]{2,}/g)]
      .map((match) => match[0])
      .filter((token) => !["the", "and", "for", "with", "that", "this", "what", "which", "who"].includes(token)),
  );
}

function lexicalScore(question: string, primitive: GraphOpsPrimitive) {
  const questionTokens = tokenSet(question);
  const textTokens = tokenSet(primitiveText(primitive));
  if (questionTokens.size === 0 || textTokens.size === 0) return 0;
  let overlap = 0;
  for (const token of questionTokens) {
    if (textTokens.has(token)) overlap += 1;
  }
  return overlap / Math.max(1, Math.min(questionTokens.size, textTokens.size));
}

function chooseStrategy(question: string) {
  const lower = question.toLowerCase();
  if (includesAny(lower, ["how many", "count", "list all", "which nodes", "cypher"])) return "text2cypher";
  if (includesAny(lower, ["theme", "overall", "dominant", "across the corpus", "main dynamics"])) return "global_community";
  if (includesAny(lower, ["when", "timeline", "before", "after", "caused", "causal", "contradiction", "who claimed"])) {
    return "vector_cypher";
  }
  if (includesAny(lower, ["exact quote", "proper noun", "rare term", "article", "section"])) return "hybrid";
  return "hybrid";
}

function cypherTemplate(strategy: RetrievalStrategy, focus: string[]) {
  if (strategy === "text2cypher") {
    return [
      "MATCH (n:TacitusCoreV1)",
      "WHERE n.workspace_id = $workspaceId AND n.primitive_type IN $primitiveFocus",
      "RETURN n.primitive_type AS type, n.id AS id, n.name AS name, n.text AS text, n.confidence AS confidence",
      "ORDER BY coalesce(n.confidence, 0) DESC LIMIT $topK",
    ].join("\n");
  }
  if (strategy === "global_community") {
    return [
      "MATCH (n:TacitusCoreV1)",
      "WHERE n.workspace_id = $workspaceId AND n.primitive_type IN ['Narrative','Claim','Event','Constraint']",
      "OPTIONAL MATCH (n)-[:GROUNDED_IN|SUPPORTED_BY]->(ev:TacitusCoreV1)",
      "RETURN n.primitive_type AS type, collect(n.text)[0..$topK] AS evidence, collect(ev.provenance_span)[0..$topK] AS quotes",
    ].join("\n");
  }
  const startingType = focus.includes("Claim") ? "Claim" : focus.includes("Event") ? "Event" : "TacitusCoreV1";
  return [
    `MATCH (node:${startingType})`,
    "WHERE node.workspace_id = $workspaceId AND coalesce(node.confidence, 1.0) >= $confidenceFloor",
    "OPTIONAL MATCH path = (node)-[*1..2]-(neighbor:TacitusCoreV1)",
    "OPTIONAL MATCH (node)-[:GROUNDED_IN|SUPPORTED_BY]->(ev:TacitusCoreV1)",
    "RETURN node {.*, labels: labels(node)} AS node, collect(DISTINCT neighbor {.*, labels: labels(neighbor)})[0..12] AS neighborhood, collect(DISTINCT ev.provenance_span)[0..8] AS quotes",
    "LIMIT $topK",
  ].join("\n");
}

export function buildGraphOpsRetrievalPlan(input: {
  question: string;
  primitives?: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
}): GraphOpsRetrievalPlan {
  const question = input.question.trim() || "What does the graph-grounded evidence support?";
  const primitives = input.primitives ?? [];
  const strategy = chooseStrategy(question);
  const primitiveFocus = inferPrimitiveFocus(question, primitives);
  const blockerSignals = input.ruleEvaluation?.signals.filter((signal) => signal.severity === "blocker") ?? [];
  const lowEvidence = primitives.filter(
    (item) =>
      !["ExtractionRun", "SourceDocument", "SourceChunk", "EvidenceSpan"].includes(item.primitive_type) &&
      !item.evidence_span_id,
  ).length;
  const routeRationale = [
    `Question routed to ${strategy} because it asks for ${
      strategy === "global_community"
        ? "global themes"
        : strategy === "text2cypher"
          ? "structured counts or lists"
          : "evidence-grounded graph context"
    }.`,
    primitiveFocus.length > 0
      ? `Primitive focus: ${primitiveFocus.join(", ")}.`
      : "Primitive focus will be inferred from Neo4j labels at execution.",
  ];
  if (blockerSignals.length > 0) routeRationale.push("Blocker rule signals require abstention unless reviewed.");
  if (lowEvidence > 0) routeRationale.push(`${lowEvidence} primitives lack direct evidence links and should not support final claims.`);

  return {
    kind: "tacitus.dialectica.retrieval_plan.v1",
    question,
    strategy,
    primitiveFocus: primitiveFocus.length > 0 ? primitiveFocus : ["Claim", "Event", "Actor"],
    traversalDepth: strategy === "text2cypher" ? 1 : 2,
    topK: strategy === "global_community" ? 12 : 8,
    sourceBudgetChars: 12000,
    confidenceFloor: blockerSignals.length > 0 ? 0.72 : 0.5,
    abstainIf: blockerSignals.map((signal) => signal.rule_id),
    requireProvenance: true,
    temporalWindow: null,
    routeRationale,
    cypherTemplate: cypherTemplate(strategy, primitiveFocus),
    contextAssembly: [
      "Retrieve candidate primitive nodes.",
      "Expand one to two graph hops for actors, evidence, constraints, commitments, and rule signals.",
      "Attach quotes from EvidenceSpan or SourceChunk nodes.",
      "Inject RuleSignal and AnswerConstraint nodes as a separate answer-constraint block.",
      "Abstain or request review when blocker rules fire or provenance is missing.",
    ],
    requiredIndexes: [
      "tacitus_core_workspace",
      "tacitus_core_primitive_type",
      "tacitus_claim_text",
      "tacitus_chunk_text",
    ],
  };
}

export function executeGraphOpsRetrievalLocally(input: {
  plan: GraphOpsRetrievalPlan;
  primitives: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
}): GraphOpsRetrievalExecution {
  const focus = new Set(input.plan.primitiveFocus);
  const evidenceById = new Map(
    input.primitives
      .filter((item) => item.primitive_type === "EvidenceSpan")
      .map((item) => [item.id, item]),
  );
  const neighborsById = new Map<string, Set<string>>();
  for (const primitive of input.primitives) {
    for (const key of ["episode_id", "actor_id", "subject_actor_id", "constrains_actor_id", "chunk_id"]) {
      const target = primitive[key];
      if (typeof target !== "string" || !target || target === primitive.id) continue;
      if (!neighborsById.has(primitive.id)) neighborsById.set(primitive.id, new Set());
      if (!neighborsById.has(target)) neighborsById.set(target, new Set());
      neighborsById.get(primitive.id)?.add(target);
      neighborsById.get(target)?.add(primitive.id);
    }
  }

  const candidates = input.primitives
    .filter((item) => focus.has(item.primitive_type))
    .filter((item) => (typeof item.confidence === "number" ? item.confidence : 1) >= input.plan.confidenceFloor)
    .map((item) => ({
      item,
      score:
        lexicalScore(input.plan.question, item) * 0.55 +
        (typeof item.confidence === "number" ? item.confidence : 0.5) * 0.35 +
        (item.evidence_span_id ? 0.1 : 0),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, input.plan.topK);

  const context = candidates.map(({ item }) => {
    const evidenceIds = typeof item.evidence_span_id === "string" ? [item.evidence_span_id] : [];
    return {
      id: item.id,
      primitiveType: item.primitive_type,
      label: primitiveLabel(item),
      confidence: typeof item.confidence === "number" ? item.confidence : null,
      text: primitiveText(item),
      evidenceIds,
      neighborIds: [...(neighborsById.get(item.id) ?? new Set<string>())].slice(0, 12),
      quoteIds: evidenceIds.filter((id) => evidenceById.has(id)),
    };
  });

  const supportsByEvidence = new Map<string, string[]>();
  for (const item of context) {
    for (const evidenceId of item.evidenceIds) {
      const existing = supportsByEvidence.get(evidenceId) ?? [];
      existing.push(item.id);
      supportsByEvidence.set(evidenceId, existing);
    }
  }

  const citations = [...supportsByEvidence.entries()]
    .map(([id, supports]) => {
      const evidence = evidenceById.get(id);
      return {
        id,
        quote: String(evidence?.provenance_span ?? evidence?.text ?? "").slice(0, 800),
        sourceId: typeof evidence?.source_id === "string" ? evidence.source_id : null,
        chunkId: typeof evidence?.chunk_id === "string" ? evidence.chunk_id : null,
        supports,
      };
    })
    .filter((item) => item.quote.length > 0)
    .slice(0, 24);

  const ruleFindings = (input.ruleEvaluation?.signals ?? [])
    .filter((signal) => signal.severity !== "info")
    .map((signal) => ({
      ruleId: signal.rule_id,
      severity: signal.severity,
      rationale: signal.rationale,
      affectedIds: signal.affected_ids,
    }));

  const blockerSignals = ruleFindings.filter((signal) => signal.severity === "blocker").length;
  const missingEvidenceItems = context.filter((item) => item.evidenceIds.length === 0).length;
  const lowConfidenceItems = context.filter((item) => (item.confidence ?? 1) < 0.7).length;
  const reasons: string[] = [];
  if (blockerSignals > 0) reasons.push("Blocker rule signals are present.");
  if (input.plan.requireProvenance && citations.length === 0) reasons.push("No cited evidence spans were retrieved.");
  if (missingEvidenceItems > 0) reasons.push(`${missingEvidenceItems} retrieved item(s) lack direct evidence links.`);

  return {
    kind: "tacitus.dialectica.retrieval_execution.v1",
    executedAt: new Date().toISOString(),
    mode: "local_primitives",
    plan: input.plan,
    answerPolicy: {
      mayAnswer: blockerSignals === 0 && (!input.plan.requireProvenance || citations.length > 0),
      reasons,
      requiredDisclosures: [
        "Cite retrieved EvidenceSpan quotes for factual claims.",
        "Separate temporal order from causal explanation.",
        "Mark low-confidence or unreviewed items as candidate facts.",
      ],
    },
    context,
    citations,
    ruleFindings,
    diagnostics: {
      contextItems: context.length,
      citations: citations.length,
      lowConfidenceItems,
      blockerSignals,
      missingEvidenceItems,
    },
  };
}
