import { runGraphOpsBenchmark, type GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import { buildDynamicOntologyPlan } from "@/lib/dynamicOntology";
import {
  extractGraphOpsPrimitives,
  sampleText,
  type GraphOpsExtractionResult,
  type GraphOpsPrimitive,
} from "@/lib/graphopsExtraction";
import { buildGraphOpsGraphWritePlan, type GraphOpsGraphWritePlan } from "@/lib/graphopsGraph";
import {
  buildGraphOpsRetrievalPlan,
  executeGraphOpsRetrievalLocally,
  type GraphOpsRetrievalExecution,
  type GraphOpsRetrievalPlan,
} from "@/lib/graphopsRetrieval";
import { evaluateNeurosymbolicRules, type RuleEvaluationResult } from "@/lib/graphopsRules";
import { buildGraphOpsTraceBundle, type GraphOpsTraceBundle } from "@/lib/graphopsTrace";
import { buildPraxisContextBundle, type PraxisContextBundle } from "@/lib/praxisContext";

export type GraphOpsDemoReadyRun = {
  kind: "tacitus.dialectica.demo_ready_run.v1";
  demoId: string;
  createdAt: string;
  title: string;
  workspaceId: string;
  caseId: string;
  objective: string;
  question: string;
  extraction: GraphOpsExtractionResult;
  ruleEvaluation: RuleEvaluationResult;
  benchmark: GraphOpsBenchmarkResult;
  graphWritePlan: Pick<GraphOpsGraphWritePlan, "kind" | "createdAt" | "workspaceId" | "caseId" | "extractionRunId" | "summary" | "warnings">;
  retrievalPlan: GraphOpsRetrievalPlan;
  retrievalExecution: GraphOpsRetrievalExecution;
  trace: GraphOpsTraceBundle;
  praxisContext: PraxisContextBundle;
  demoReadiness: {
    status: "ready" | "review" | "blocked";
    score: number;
    wins: string[];
    gaps: string[];
    script: Array<{ timestamp: string; scene: string; proof: string }>;
  };
};

function demoStatus(score: number, blockers: number, reviewItems: number): "ready" | "review" | "blocked" {
  if (blockers > 0 || score < 0.5) return "blocked";
  if (reviewItems > 0 || score < 0.78) return "review";
  return "ready";
}

function graphPreviewFromPrimitives(primitives: GraphOpsPrimitive[]): GraphOpsExtractionResult["graphPreview"] {
  const nodes = primitives
    .filter((item) => !["SourceChunk", "ExtractionRun"].includes(item.primitive_type))
    .slice(0, 80)
    .map((item) => ({
      id: item.id,
      label: item.primitive_type,
      node_type: item.primitive_type.toLowerCase(),
      name: String(item.name ?? item.title ?? item.description ?? item.text ?? item.primitive_type).slice(0, 80),
      confidence: item.confidence,
    }));
  const links = primitives
    .flatMap((item) => {
      const edges: GraphOpsExtractionResult["graphPreview"]["links"] = [];
      for (const [key, edgeType] of [
        ["evidence_span_id", "EVIDENCED_BY"],
        ["document_id", "FROM_DOCUMENT"],
        ["chunk_id", "FROM_CHUNK"],
        ["episode_id", "IN_EPISODE"],
        ["actor_id", "ABOUT_ACTOR"],
        ["subject_actor_id", "ABOUT_ACTOR"],
        ["constrains_actor_id", "CONSTRAINS"],
      ] as const) {
        const target = item[key];
        if (typeof target === "string" && target && target !== item.id) {
          edges.push({
            id: `edge_${item.id}_${edgeType}_${target}`.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 128),
            source: item.id,
            target,
            edge_type: edgeType,
            confidence: item.confidence,
          });
        }
      }
      return edges;
    })
    .slice(0, 160);
  return { nodes, links };
}

function extractionFromPrimitives(input: {
  primitives: GraphOpsPrimitive[];
  workspaceId: string;
  caseId: string;
  objective: string;
  ontologyProfile: string;
  sourceType: string;
}): GraphOpsExtractionResult {
  const counts = input.primitives.reduce<Record<string, number>>((acc, primitive) => {
    acc[primitive.primitive_type] = (acc[primitive.primitive_type] ?? 0) + 1;
    return acc;
  }, {});
  const extractionRun =
    input.primitives.find((item) => item.primitive_type === "ExtractionRun") ?? input.primitives[0];
  const chunks = input.primitives.filter((item) => item.primitive_type === "SourceChunk");
  const textChars = chunks.reduce((sum, item) => sum + String(item.text ?? "").length, 0);
  const dynamicOntology = buildDynamicOntologyPlan({
    profileId: input.ontologyProfile,
    objective: input.objective,
    sourceType: input.sourceType,
  });
  const evidenceCount = counts.EvidenceSpan ?? 0;
  const claimLikeCount =
    (counts.Claim ?? 0) + (counts.Constraint ?? 0) + (counts.Commitment ?? 0) + (counts.Event ?? 0);
  const evidenceCoverage = claimLikeCount > 0 ? Math.min(evidenceCount / claimLikeCount, 1) : 0;

  return {
    workspaceId: input.workspaceId,
    caseId: input.caseId,
    objective: input.objective,
    ontologyProfile: input.ontologyProfile,
    extractionRunId: String(extractionRun?.extraction_run_id || extractionRun?.id || `run_${input.caseId}`),
    dynamicOntology,
    preExtraction: {
      originalChars: textChars,
      cleanedChars: textChars,
      removedSections: [],
      segmentCount: Math.max(counts.Episode ?? chunks.length, chunks.length, 1),
      segmentationMode: "provided_extraction",
      segments: chunks.slice(0, 12).map((chunk, index) => ({
        id: String(chunk.segment_id || chunk.id),
        label: String(chunk.name || `Provided chunk ${index + 1}`),
        start: Number(chunk.start_char ?? 0),
        end: Number(chunk.end_char ?? String(chunk.text ?? "").length),
        charCount: String(chunk.text ?? "").length,
        reason: "provided_extraction",
      })),
    },
    graphWrite: {
      requested: false,
      enabled: false,
      written: 0,
      message: "Preview only.",
    },
    counts,
    quality: {
      status: evidenceCoverage >= 0.65 && claimLikeCount > 0 ? "ready" : "review",
      score: Math.round((evidenceCoverage * 70 + Math.min(input.primitives.length, 30)) * 10) / 10,
      evidenceCoverage,
      actorCount: counts.Actor ?? 0,
      issueCount: claimLikeCount,
      recommendations:
        evidenceCoverage >= 0.65
          ? ["Provided extraction is structured enough for a demo retrieval pass."]
          : ["Review evidence coverage before using this extraction in a final demo."],
    },
    primitives: input.primitives,
    graphPreview: graphPreviewFromPrimitives(input.primitives),
    nextQuestions: [
      "Which primitives need analyst review before Praxis consumes them?",
      "Which claims or constraints lack evidence?",
      "Which graph relationships should be promoted to Neo4j first?",
      "What should the benchmark assert for this run?",
      "Which answer should be traced for a demo recording?",
    ],
  };
}

export function buildGraphOpsDemoReadyRun(input: {
  text?: string;
  sampleKey?: string;
  extraction?: GraphOpsExtractionResult;
  primitives?: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
  workspaceId?: string;
  caseId?: string;
  objective?: string;
  ontologyProfile?: string;
  sourceTitle?: string;
  sourceType?: string;
  question?: string;
  answerDraft?: string;
}): GraphOpsDemoReadyRun {
  const selectedSampleKey = input.sampleKey || "policy-constraint-map";
  const workspaceId = input.workspaceId || "demo-policy-friction-lab";
  const caseId = input.caseId || selectedSampleKey;
  const objective =
    input.objective ||
    "Run a demo-ready DIALECTICA pipeline from source text to graph-grounded context.";
  const ontologyProfile = input.ontologyProfile || "policy-analysis";
  const question =
    input.question || "Which constraints block feasible policy options, and what should an analyst verify next?";
  const answerDraft =
    input.answerDraft ||
    "DIALECTICA should identify binding constraints, cite evidence spans, and surface review questions before final recommendations.";

  const providedPrimitives = Array.isArray(input.primitives) ? input.primitives : [];
  const extraction =
    input.extraction ??
    (providedPrimitives.length > 0
      ? extractionFromPrimitives({
          primitives: providedPrimitives,
          workspaceId,
          caseId,
          objective,
          ontologyProfile,
          sourceType: input.sourceType || "provided-extraction",
        })
      : (() => {
          const text = (input.text || sampleText(selectedSampleKey) || "").trim();
          if (!text) {
            throw new Error("Provide extraction, primitives, text, or a valid sampleKey for a demo-ready run.");
          }
          return extractGraphOpsPrimitives({
            text: text.slice(0, 120000),
            workspaceId,
            caseId,
            objective,
            ontologyProfile,
            sourceTitle: input.sourceTitle || "Demo source",
            sourceType: input.sourceType || "text",
          });
        })());
  const ruleEvaluation = input.ruleEvaluation ?? evaluateNeurosymbolicRules(extraction.primitives);
  const benchmark = runGraphOpsBenchmark({
    workspaceId,
    caseId,
    extractionRunId: extraction.extractionRunId,
    objective,
    question,
    answer: answerDraft,
    primitives: extraction.primitives,
    ruleEvaluation,
  });
  const graphWritePlan = buildGraphOpsGraphWritePlan({
    primitives: extraction.primitives,
    ruleEvaluation,
    benchmark,
  });
  const retrievalPlan = buildGraphOpsRetrievalPlan({
    question,
    primitives: extraction.primitives,
    ruleEvaluation,
  });
  const retrievalExecution = executeGraphOpsRetrievalLocally({
    plan: retrievalPlan,
    primitives: extraction.primitives,
    ruleEvaluation,
  });
  const trace = buildGraphOpsTraceBundle({
    question,
    answerDraft,
    primitives: extraction.primitives,
    ruleEvaluation,
    retrievalPlan,
    benchmark,
  });
  const praxisContext = buildPraxisContextBundle({
    workspaceId,
    caseId,
    extractionRunId: extraction.extractionRunId,
    objective,
    primitives: extraction.primitives,
    ruleEvaluation,
    benchmark,
    nextQuestions: extraction.nextQuestions,
  });

  const blockers = ruleEvaluation.summary.blocker + (retrievalExecution.answerPolicy.mayAnswer ? 0 : 1);
  const score = Math.round(
    ((benchmark.scores.overall * 0.35 +
      praxisContext.readiness.score * 0.25 +
      (retrievalExecution.answerPolicy.mayAnswer ? 1 : 0.45) * 0.2 +
      Math.min(graphWritePlan.summary.edges / Math.max(graphWritePlan.summary.nodes, 1), 2) / 2 * 0.2) *
      100),
  ) / 100;
  const gaps: string[] = [];
  if (!retrievalExecution.answerPolicy.mayAnswer) gaps.push("Retrieval answer policy requires review before final answer.");
  if (ruleEvaluation.summary.review > 0) gaps.push(`${ruleEvaluation.summary.review} rule signal(s) require analyst review.`);
  if (benchmark.scores.overall < 0.8) gaps.push("Benchmark score is below demo-ready threshold; show it as review-mode, not final-mode.");
  if (graphWritePlan.warnings.length > 0) gaps.push("Graph write plan skipped some relationships to missing nodes.");

  return {
    kind: "tacitus.dialectica.demo_ready_run.v1",
    demoId: `demo_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`,
    createdAt: new Date().toISOString(),
    title: "DIALECTICA demo-ready GraphRAG run",
    workspaceId,
    caseId,
    objective,
    question,
    extraction,
    ruleEvaluation,
    benchmark,
    graphWritePlan: {
      kind: graphWritePlan.kind,
      createdAt: graphWritePlan.createdAt,
      workspaceId: graphWritePlan.workspaceId,
      caseId: graphWritePlan.caseId,
      extractionRunId: graphWritePlan.extractionRunId,
      summary: graphWritePlan.summary,
      warnings: graphWritePlan.warnings,
    },
    retrievalPlan,
    retrievalExecution,
    trace,
    praxisContext,
    demoReadiness: {
      status: demoStatus(score, blockers, gaps.length),
      score,
      wins: [
        `${extraction.primitives.length} typed primitives extracted with source structure.`,
        `${graphWritePlan.summary.nodes} graph nodes and ${graphWritePlan.summary.edges} graph relationships planned.`,
        `${retrievalExecution.diagnostics.contextItems} context items and ${retrievalExecution.diagnostics.citations} citations retrieved.`,
        `${trace.ruleFindings.length} rule finding(s) attached to the analyst trace.`,
      ],
      gaps,
      script: [
        {
          timestamp: "0:00",
          scene: "Ingest and structure",
          proof: `${extraction.counts.Actor ?? 0} actors, ${extraction.counts.Claim ?? 0} claims, ${extraction.counts.Constraint ?? 0} constraints.`,
        },
        {
          timestamp: "0:45",
          scene: "Graph memory",
          proof: `${graphWritePlan.summary.nodes} nodes / ${graphWritePlan.summary.edges} edges in the write plan.`,
        },
        {
          timestamp: "1:30",
          scene: "Graph-grounded retrieval",
          proof: `${retrievalPlan.strategy} route with ${retrievalExecution.diagnostics.citations} cited evidence span(s).`,
        },
        {
          timestamp: "2:15",
          scene: "Trace and rules",
          proof: `${ruleEvaluation.summary.fired} rule signal(s), ${praxisContext.reviewQueue.length} review item(s).`,
        },
        {
          timestamp: "3:00",
          scene: "Praxis handoff",
          proof: `Praxis context status ${praxisContext.readiness.status} at ${Math.round(praxisContext.readiness.score * 100)}%.`,
        },
      ],
    },
  };
}
