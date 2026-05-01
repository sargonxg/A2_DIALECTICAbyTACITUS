import type { GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";
import type { GraphOpsRetrievalPlan } from "@/lib/graphopsRetrieval";

export type GraphOpsTraceBundle = {
  kind: "tacitus.dialectica.answer_trace.v1";
  traceId: string;
  createdAt: string;
  question: string;
  answerDraft: string;
  retrievalPlan: GraphOpsRetrievalPlan;
  graphContext: {
    nodes: Array<{ id: string; type: string; label: string; confidence: number | null }>;
    edges: Array<{ source: string; target: string; type: string; confidence: number | null }>;
  };
  citations: Array<{
    evidenceId: string;
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
    recommendedAction: string;
  }>;
  benchmarkSummary?: {
    overall: number;
    evidenceGrounding: number;
    causalDiscipline: number;
    ruleCompliance: number;
    status: string;
  };
  analystInstructions: string[];
};

function labelFor(item: GraphOpsPrimitive) {
  return String(item.name ?? item.title ?? item.text ?? item.description ?? item.content ?? item.primitive_type).slice(
    0,
    120,
  );
}

export function buildGraphOpsTraceBundle(input: {
  question: string;
  answerDraft?: string;
  primitives: GraphOpsPrimitive[];
  ruleEvaluation: RuleEvaluationResult;
  retrievalPlan: GraphOpsRetrievalPlan;
  benchmark?: GraphOpsBenchmarkResult;
}): GraphOpsTraceBundle {
  const evidence = input.primitives.filter((item) => item.primitive_type === "EvidenceSpan");
  const evidenceById = new Map(evidence.map((item) => [item.id, item]));
  const citedByEvidence = new Map<string, string[]>();
  for (const primitive of input.primitives) {
    if (primitive.evidence_span_id) {
      const existing = citedByEvidence.get(primitive.evidence_span_id) ?? [];
      existing.push(primitive.id);
      citedByEvidence.set(primitive.evidence_span_id, existing);
    }
  }

  const nodes = input.primitives
    .filter((item) => !["ExtractionRun", "SourceDocument"].includes(item.primitive_type))
    .slice(0, 60)
    .map((item) => ({
      id: item.id,
      type: item.primitive_type,
      label: labelFor(item),
      confidence: typeof item.confidence === "number" ? item.confidence : null,
    }));

  const edges = input.primitives
    .flatMap((item) => {
      const output: Array<{ source: string; target: string; type: string; confidence: number | null }> = [];
      for (const [key, type] of [
        ["evidence_span_id", "GROUNDED_IN"],
        ["episode_id", "IN_EPISODE"],
        ["actor_id", "ABOUT_ACTOR"],
        ["subject_actor_id", "MADE_BY"],
        ["constrains_actor_id", "CONSTRAINS"],
      ] as const) {
        const target = item[key];
        if (typeof target === "string" && target && target !== item.id) {
          output.push({
            source: item.id,
            target,
            type,
            confidence: typeof item.confidence === "number" ? item.confidence : null,
          });
        }
      }
      return output;
    })
    .slice(0, 100);

  const citations = [...citedByEvidence.entries()]
    .map(([evidenceId, supports]) => {
      const item = evidenceById.get(evidenceId);
      return {
        evidenceId,
        quote: String(item?.provenance_span ?? item?.text ?? "").slice(0, 600),
        sourceId: typeof item?.source_id === "string" ? item.source_id : null,
        chunkId: typeof item?.chunk_id === "string" ? item.chunk_id : null,
        supports: supports.slice(0, 12),
      };
    })
    .filter((item) => item.quote)
    .slice(0, 20);

  return {
    kind: "tacitus.dialectica.answer_trace.v1",
    traceId: `trace_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`,
    createdAt: new Date().toISOString(),
    question: input.question,
    answerDraft: input.answerDraft ?? "",
    retrievalPlan: input.retrievalPlan,
    graphContext: { nodes, edges },
    citations,
    ruleFindings: input.ruleEvaluation.signals.map((signal) => ({
      ruleId: signal.rule_id,
      severity: signal.severity,
      rationale: signal.rationale,
      affectedIds: signal.affected_ids,
      recommendedAction: signal.recommended_action,
    })),
    benchmarkSummary: input.benchmark
      ? {
          overall: input.benchmark.scores.overall,
          evidenceGrounding: input.benchmark.scores.evidenceGrounding,
          causalDiscipline: input.benchmark.scores.causalDiscipline,
          ruleCompliance: input.benchmark.scores.ruleCompliance,
          status:
            input.benchmark.scores.overall >= 0.8
              ? "ready"
              : input.benchmark.scores.overall >= 0.6
                ? "review"
                : "blocked",
        }
      : undefined,
    analystInstructions: [
      "Check every final answer sentence against citations before publishing.",
      "Treat blocker rule signals as abstention conditions until a human review decision exists.",
      "Do not promote temporal sequence to causality unless a rule signal or source span supports it.",
      "Promote recurring failures into benchmark items rather than relying on ad hoc prompt edits.",
    ],
  };
}
