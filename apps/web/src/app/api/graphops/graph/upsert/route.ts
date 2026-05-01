import { NextResponse } from "next/server";
import { runGraphOpsBenchmark, type GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import { extractGraphOpsPrimitives, sampleText, type GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { buildGraphOpsGraphWritePlan, writeGraphOpsPlanToNeo4j } from "@/lib/graphopsGraph";
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
  let ruleEvaluation = coerceRuleEvaluation(body.ruleEvaluation);
  let benchmark = coerceBenchmark(body.benchmark);
  let workspaceId = String(body.workspaceId || "graphops-workspace");
  let caseId = String(body.caseId || "graphops-case");
  let objective = String(body.objective || "Write a DIALECTICA graph-ready run to Neo4j.");
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
      sourceTitle: String(body.sourceTitle || "GraphOps graph source"),
      sourceType: String(body.sourceType || "text"),
    });
    primitives = extraction.primitives;
    extractionRunId = extraction.extractionRunId;
  }

  ruleEvaluation = ruleEvaluation ?? evaluateNeurosymbolicRules(primitives);
  if (!benchmark && body.includeBenchmark) {
    benchmark = runGraphOpsBenchmark({
      workspaceId,
      caseId,
      extractionRunId,
      objective,
      question: String(body.question || "What should the graph-grounded answer prove?"),
      answer: String(body.answer || ""),
      primitives,
      ruleEvaluation,
    });
  }

  const plan = buildGraphOpsGraphWritePlan({ primitives, ruleEvaluation, benchmark });
  if (body.dryRun === true) {
    return NextResponse.json({
      mode: "dry_run",
      plan,
      write: {
        requested: false,
        enabled: false,
        written: 0,
        relationships: 0,
        message: "Dry run only. Set dryRun=false or omit dryRun to write to Neo4j.",
      },
    });
  }

  const write = await writeGraphOpsPlanToNeo4j(plan);
  return NextResponse.json({
    mode: "graph_writeback",
    plan: {
      kind: plan.kind,
      createdAt: plan.createdAt,
      workspaceId: plan.workspaceId,
      caseId: plan.caseId,
      extractionRunId: plan.extractionRunId,
      summary: plan.summary,
      warnings: plan.warnings,
    },
    write,
  });
}
