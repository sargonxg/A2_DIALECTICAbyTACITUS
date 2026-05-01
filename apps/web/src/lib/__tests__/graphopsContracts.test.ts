import { describe, expect, it } from "@jest/globals";
import { buildGraphOpsDemoReadyRun } from "@/lib/graphopsDemo";
import { buildGraphOpsGraphWritePlan, GRAPHOPS_SCHEMA_STATEMENTS } from "@/lib/graphopsGraph";
import { buildGraphOpsPromoStudioRun } from "@/lib/graphopsPromo";
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

describe("GraphOps demo-ready contract", () => {
  it("assembles extraction, graph plan, retrieval, trace, benchmark, and Praxis context", () => {
    const demo = buildGraphOpsDemoReadyRun({
      sampleKey: "policy-constraint-map",
      workspaceId: "demo-ws",
      caseId: "demo-case",
      question: "Which constraints block feasible policy options?",
    });

    expect(demo.kind).toBe("tacitus.dialectica.demo_ready_run.v1");
    expect(demo.extraction.primitives.length).toBeGreaterThan(10);
    expect(demo.graphWritePlan.summary.nodes).toBeGreaterThan(10);
    expect(demo.retrievalExecution.diagnostics.contextItems).toBeGreaterThan(0);
    expect(demo.trace.kind).toBe("tacitus.dialectica.answer_trace.v1");
    expect(demo.praxisContext.kind).toBe("tacitus.dialectica.praxis_context.v1");
    expect(demo.demoReadiness.script).toHaveLength(5);
  });
});

describe("GraphOps promo studio contract", () => {
  it("assembles a recordable promo script with live API and Praxis proof", async () => {
    const promo = await buildGraphOpsPromoStudioRun({
      sampleKey: "policy-constraint-map",
      workspaceId: "demo-ws",
      caseId: "promo-case",
      question: "Which constraints block feasible policy options?",
      command: "Create a policy conflict promo with ontology, GraphRAG, benchmark, and Praxis handoff.",
    });

    expect(promo.kind).toBe("tacitus.dialectica.promo_studio.v1");
    expect(promo.demoRun.kind).toBe("tacitus.dialectica.demo_ready_run.v1");
    expect(promo.aiPlan.mode).toMatch(/planner|assisted/);
    expect(promo.liveChecks.length).toBeGreaterThanOrEqual(5);
    expect(promo.apiProof.some((item) => item.endpoint === "/api/graphops/praxis/context")).toBe(true);
    expect(promo.recordingScript).toHaveLength(6);
    expect(promo.wowMoments.length).toBeGreaterThanOrEqual(4);
  });
});
