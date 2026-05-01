import { NextResponse } from "next/server";
import { runGraphOpsBenchmark, type GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import { extractGraphOpsPrimitives, sampleText, type GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { readGraphOpsRun } from "@/lib/graphopsRuns";
import { evaluateNeurosymbolicRules, type RuleEvaluationResult } from "@/lib/graphopsRules";
import { buildGraphOpsRetrievalPlan, type GraphOpsRetrievalPlan } from "@/lib/graphopsRetrieval";
import { buildGraphOpsTraceBundle } from "@/lib/graphopsTrace";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function coerceRuleEvaluation(value: unknown): RuleEvaluationResult | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<RuleEvaluationResult>;
  return candidate.mode === "deterministic_neurosymbolic_rules" && Array.isArray(candidate.signals)
    ? (candidate as RuleEvaluationResult)
    : undefined;
}

function coerceBenchmark(value: unknown): GraphOpsBenchmarkResult | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<GraphOpsBenchmarkResult>;
  return candidate.mode === "deterministic_graphops_benchmark" && Boolean(candidate.scores)
    ? (candidate as GraphOpsBenchmarkResult)
    : undefined;
}

function coerceRetrievalPlan(value: unknown): GraphOpsRetrievalPlan | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<GraphOpsRetrievalPlan>;
  return candidate.kind === "tacitus.dialectica.retrieval_plan.v1" && Boolean(candidate.strategy)
    ? (candidate as GraphOpsRetrievalPlan)
    : undefined;
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  let primitives = Array.isArray(body.primitives) ? (body.primitives as GraphOpsPrimitive[]) : [];
  let ruleEvaluation = coerceRuleEvaluation(body.ruleEvaluation);
  let benchmark = coerceBenchmark(body.benchmark);
  const question = String(body.question || "What does the graph-grounded evidence support?");
  const answerDraft = String(body.answerDraft || body.answer || "");
  let retrievalPlan = coerceRetrievalPlan(body.retrievalPlan);
  let workspaceId = String(body.workspaceId || "trace-workspace");
  let caseId = String(body.caseId || "trace-case");
  let objective = String(body.objective || "Build an analyst-readable answer trace.");
  let extractionRunId = String(body.extractionRunId || "");

  if (extractionRunId && primitives.length === 0) {
    const run = (await readGraphOpsRun(extractionRunId)) as Record<string, unknown>;
    primitives = Array.isArray(run.primitives) ? (run.primitives as GraphOpsPrimitive[]) : [];
    workspaceId = String(run.workspaceId || workspaceId);
    caseId = String(run.caseId || caseId);
    objective = String(run.objective || objective);
    extractionRunId = String(run.extractionRunId || extractionRunId);
    ruleEvaluation = coerceRuleEvaluation(run.ruleEvaluation) ?? ruleEvaluation;
  }

  if (primitives.length === 0) {
    const text = String(body.text || sampleText(String(body.sampleKey || "")) || "");
    if (!text.trim()) {
      return NextResponse.json(
        { error: "Provide primitives, extractionRunId, text, or sampleKey." },
        { status: 400 },
      );
    }
    const extraction = extractGraphOpsPrimitives({
      text: text.slice(0, 120000),
      workspaceId,
      caseId,
      objective,
      ontologyProfile: String(body.ontologyProfile || "human-friction"),
      sourceTitle: String(body.sourceTitle || "Trace source"),
      sourceType: String(body.sourceType || "text"),
    });
    primitives = extraction.primitives;
    extractionRunId = extraction.extractionRunId;
  }

  ruleEvaluation = ruleEvaluation ?? evaluateNeurosymbolicRules(primitives);
  retrievalPlan = retrievalPlan ?? buildGraphOpsRetrievalPlan({ question, primitives, ruleEvaluation });
  benchmark =
    benchmark ??
    (body.includeBenchmark === false
      ? undefined
      : runGraphOpsBenchmark({
          workspaceId,
          caseId,
          extractionRunId,
          objective,
          question,
          answer: answerDraft,
          primitives,
          ruleEvaluation,
        }));

  return NextResponse.json(
    buildGraphOpsTraceBundle({
      question,
      answerDraft,
      primitives,
      ruleEvaluation,
      retrievalPlan,
      benchmark,
    }),
  );
}
