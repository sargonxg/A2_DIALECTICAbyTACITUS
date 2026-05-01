import { NextResponse } from "next/server";
import { extractGraphOpsPrimitives, sampleText, type GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { runGraphOpsBenchmark } from "@/lib/graphopsBenchmark";
import { listGraphOpsBenchmarks, persistGraphOpsBenchmark } from "@/lib/graphopsBenchmarkRuns";
import { readGraphOpsRun } from "@/lib/graphopsRuns";
import { evaluateNeurosymbolicRules, type RuleEvaluationResult } from "@/lib/graphopsRules";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function coerceRuleEvaluation(value: unknown): RuleEvaluationResult | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<RuleEvaluationResult>;
  if (candidate.mode === "deterministic_neurosymbolic_rules" && Array.isArray(candidate.signals)) {
    return candidate as RuleEvaluationResult;
  }
  return undefined;
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const limit = Number(url.searchParams.get("limit") ?? "20");
  return NextResponse.json({ benchmarks: await listGraphOpsBenchmarks(Number.isFinite(limit) ? limit : 20) });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  let primitives = Array.isArray(body.primitives) ? (body.primitives as GraphOpsPrimitive[]) : [];
  let workspaceId = String(body.workspaceId || "graphops-workspace");
  let caseId = String(body.caseId || "graphops-case");
  let objective = String(body.objective || "Understand the conflict");
  let extractionRunId = String(body.extractionRunId || "");
  let ruleEvaluation = coerceRuleEvaluation(body.ruleEvaluation);

  if (body.extractionRunId && primitives.length === 0) {
    const run = (await readGraphOpsRun(String(body.extractionRunId))) as Record<string, unknown>;
    primitives = Array.isArray(run.primitives) ? (run.primitives as GraphOpsPrimitive[]) : [];
    workspaceId = String(run.workspaceId || workspaceId);
    caseId = String(run.caseId || caseId);
    objective = String(run.objective || objective);
    extractionRunId = String(run.extractionRunId || body.extractionRunId);
    ruleEvaluation = coerceRuleEvaluation(run.ruleEvaluation);
  }

  if (primitives.length === 0) {
    const text = String(body.text || sampleText(String(body.sampleKey || "romeo-juliet-conflict")) || "");
    if (!text.trim()) {
      return NextResponse.json({ error: "Provide primitives, extractionRunId, text, or sampleKey." }, { status: 400 });
    }
    const extraction = extractGraphOpsPrimitives({
      text: text.slice(0, 120000),
      workspaceId,
      caseId,
      objective,
      ontologyProfile: String(body.ontologyProfile || "literary-conflict"),
      sourceTitle: String(body.sourceTitle || "Benchmark source"),
      sourceType: String(body.sourceType || "text"),
    });
    primitives = extraction.primitives;
    extractionRunId = extraction.extractionRunId;
    ruleEvaluation = evaluateNeurosymbolicRules(primitives);
  }

  if (primitives.length === 0) {
    return NextResponse.json({ error: "No primitives available for benchmark scoring." }, { status: 400 });
  }

  const result = runGraphOpsBenchmark({
    workspaceId,
    caseId,
    extractionRunId,
    objective,
    question: String(body.question || "What does the graph prove, what remains uncertain, and what should Praxis ask next?"),
    answer: String(body.answer || ""),
    goldAnswer: body.goldAnswer ? String(body.goldAnswer) : undefined,
    expectedPrimitiveTypes: Array.isArray(body.expectedPrimitiveTypes)
      ? body.expectedPrimitiveTypes.map(String)
      : undefined,
    primitives,
    ruleEvaluation: ruleEvaluation ?? evaluateNeurosymbolicRules(primitives),
  });
  const localPersistence = await persistGraphOpsBenchmark(result);

  return NextResponse.json({ ...result, localPersistence });
}
