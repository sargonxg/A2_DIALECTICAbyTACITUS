import { describe, expect, it } from "@jest/globals";
import { buildGraphOpsGraphWritePlan, GRAPHOPS_SCHEMA_STATEMENTS } from "@/lib/graphopsGraph";
import {
  buildGraphOpsRetrievalPlan,
  executeGraphOpsRetrievalLocally,
} from "@/lib/graphopsRetrieval";
import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

const primitives: GraphOpsPrimitive[] = [
  {
    id: "run_test",
    primitive_type: "ExtractionRun",
    workspace_id: "ws",
    case_id: "case",
    source_id: "source_1",
    extraction_run_id: "run_test",
    ontology_version: "tacitus_core_v1",
    confidence: 1,
    observed_at: "2026-05-01T00:00:00.000Z",
  },
  {
    id: "chunk_1",
    primitive_type: "SourceChunk",
    workspace_id: "ws",
    case_id: "case",
    source_id: "source_1",
    extraction_run_id: "run_test",
    ontology_version: "tacitus_core_v1",
    confidence: 1,
    observed_at: "2026-05-01T00:00:00.000Z",
    text: "The Housing Agency must publish eligibility rules before the July deadline.",
  },
  {
    id: "span_1",
    primitive_type: "EvidenceSpan",
    workspace_id: "ws",
    case_id: "case",
    source_id: "source_1",
    extraction_run_id: "run_test",
    ontology_version: "tacitus_core_v1",
    confidence: 0.9,
    observed_at: "2026-05-01T00:00:00.000Z",
    chunk_id: "chunk_1",
    provenance_span: "The Housing Agency must publish eligibility rules before the July deadline.",
  },
  {
    id: "actor_1",
    primitive_type: "Actor",
    workspace_id: "ws",
    case_id: "case",
    source_id: "source_1",
    extraction_run_id: "run_test",
    ontology_version: "tacitus_core_v1",
    confidence: 0.88,
    observed_at: "2026-05-01T00:00:00.000Z",
    evidence_span_id: "span_1",
    name: "Housing Agency",
  },
  {
    id: "constraint_1",
    primitive_type: "Constraint",
    workspace_id: "ws",
    case_id: "case",
    source_id: "source_1",
    extraction_run_id: "run_test",
    ontology_version: "tacitus_core_v1",
    confidence: 0.84,
    observed_at: "2026-05-01T00:00:00.000Z",
    evidence_span_id: "span_1",
    actor_id: "actor_1",
    description: "Eligibility rules must be published before the July deadline.",
  },
];

const ruleEvaluation: RuleEvaluationResult = {
  mode: "deterministic_neurosymbolic_rules",
  summary: { fired: 1, review: 1, warning: 0, blocker: 0 },
  signals: [
    {
      id: "signal_1",
      rule_id: "legal-constraint-option-filter",
      rule_name: "Legal Constraint Option Filter",
      category: "policy",
      severity: "review",
      status: "fired",
      rationale: "Normative or procedural constraints were detected.",
      evidence_ids: ["span_1"],
      affected_ids: ["constraint_1"],
      recommended_action: "Filter options against the deadline.",
      benchmark_target: "policy_constraint_accuracy",
    },
  ],
  answerConstraints: ["Do not suggest options that violate explicit deadlines."],
  benchmarkTargets: ["policy_constraint_accuracy"],
};

describe("GraphOps graph contracts", () => {
  it("builds deterministic node and edge identities for idempotent graph writeback", () => {
    const first = buildGraphOpsGraphWritePlan({ primitives, ruleEvaluation });
    const second = buildGraphOpsGraphWritePlan({ primitives, ruleEvaluation });

    expect(first.summary.nodes).toBe(second.summary.nodes);
    expect(first.summary.edges).toBe(second.summary.edges);
    expect(first.nodes.map((item) => item.id).sort()).toEqual(second.nodes.map((item) => item.id).sort());
    expect(first.edges.map((item) => item.id).sort()).toEqual(second.edges.map((item) => item.id).sort());
    expect(first.edges.some((item) => item.type === "GROUNDED_IN" && item.target === "span_1")).toBe(true);
    expect(first.nodes.some((item) => item.primitiveType === "ReviewDecision")).toBe(true);
  });

  it("keeps runtime schema requirements available to migrations", () => {
    expect(GRAPHOPS_SCHEMA_STATEMENTS).toEqual(
      expect.arrayContaining([
        expect.stringContaining("tacitus_core_v1_id"),
        expect.stringContaining("tacitus_core_workspace"),
        expect.stringContaining("tacitus_claim_text"),
      ]),
    );
  });
});

describe("GraphOps retrieval contracts", () => {
  it("executes local retrieval with cited context and answer policy", () => {
    const plan = buildGraphOpsRetrievalPlan({
      question: "Which constraints block feasible policy options?",
      primitives,
      ruleEvaluation,
    });
    const execution = executeGraphOpsRetrievalLocally({ plan, primitives, ruleEvaluation });

    expect(execution.kind).toBe("tacitus.dialectica.retrieval_execution.v1");
    expect(execution.mode).toBe("local_primitives");
    expect(execution.plan.strategy).toBe("hybrid");
    expect(execution.context.some((item) => item.primitiveType === "Constraint")).toBe(true);
    expect(execution.citations).toHaveLength(1);
    expect(execution.answerPolicy.mayAnswer).toBe(true);
  });
});
