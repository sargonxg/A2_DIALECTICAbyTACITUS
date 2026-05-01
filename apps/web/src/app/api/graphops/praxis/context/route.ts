import { NextResponse } from "next/server";
import { runGraphOpsBenchmark, type GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import { extractGraphOpsPrimitives, sampleText, type GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { buildPraxisContextBundle } from "@/lib/praxisContext";
import { readGraphOpsRun } from "@/lib/graphopsRuns";
import { evaluateNeurosymbolicRules, type RuleEvaluationResult } from "@/lib/graphopsRules";

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

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  let primitives = Array.isArray(body.primitives) ? (body.primitives as GraphOpsPrimitive[]) : [];
  let workspaceId = String(body.workspaceId || "praxis-workspace");
  let caseId = String(body.caseId || "praxis-case");
  let objective = String(body.objective || "Prepare a provenance-grounded Praxis context.");
  let extractionRunId = String(body.extractionRunId || "");
  let nextQuestions = Array.isArray(body.nextQuestions) ? body.nextQuestions.map(String) : [];
  let ruleEvaluation = coerceRuleEvaluation(body.ruleEvaluation);
  let benchmark = coerceBenchmark(body.benchmark);

  if (body.extractionRunId && primitives.length === 0) {
    const run = (await readGraphOpsRun(String(body.extractionRunId))) as Record<string, unknown>;
    primitives = Array.isArray(run.primitives) ? (run.primitives as GraphOpsPrimitive[]) : [];
    workspaceId = String(run.workspaceId || workspaceId);
    caseId = String(run.caseId || caseId);
    objective = String(run.objective || objective);
    extractionRunId = String(run.extractionRunId || extractionRunId);
    nextQuestions = Array.isArray(run.nextQuestions) ? run.nextQuestions.map(String) : nextQuestions;
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
      sourceTitle: String(body.sourceTitle || "Praxis context source"),
      sourceType: String(body.sourceType || "text"),
    });
    primitives = extraction.primitives;
    extractionRunId = extraction.extractionRunId;
    nextQuestions = extraction.nextQuestions;
    ruleEvaluation = evaluateNeurosymbolicRules(primitives);
  }

  ruleEvaluation = ruleEvaluation ?? evaluateNeurosymbolicRules(primitives);
  if (!benchmark && body.includeBenchmark !== false) {
    benchmark = runGraphOpsBenchmark({
      workspaceId,
      caseId,
      extractionRunId,
      objective,
      question: String(
        body.question || "What should Praxis know, what remains uncertain, and what should it ask next?",
      ),
      answer: String(body.answer || ""),
      primitives,
      ruleEvaluation,
    });
  }

  return NextResponse.json(
    buildPraxisContextBundle({
      workspaceId,
      caseId,
      extractionRunId,
      objective,
      primitives,
      ruleEvaluation,
      benchmark,
      nextQuestions,
    }),
  );
}
