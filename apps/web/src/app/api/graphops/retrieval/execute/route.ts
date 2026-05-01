import { NextResponse } from "next/server";
import { extractGraphOpsPrimitives, sampleText, type GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { readGraphOpsRun } from "@/lib/graphopsRuns";
import { evaluateNeurosymbolicRules, type RuleEvaluationResult } from "@/lib/graphopsRules";
import {
  buildGraphOpsRetrievalPlan,
  executeGraphOpsRetrievalLocally,
  type GraphOpsRetrievalPlan,
} from "@/lib/graphopsRetrieval";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function coerceRuleEvaluation(value: unknown): RuleEvaluationResult | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<RuleEvaluationResult>;
  return candidate.mode === "deterministic_neurosymbolic_rules" && Array.isArray(candidate.signals)
    ? (candidate as RuleEvaluationResult)
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
  let retrievalPlan = coerceRetrievalPlan(body.retrievalPlan);
  const question = String(body.question || retrievalPlan?.question || "What does the graph-grounded evidence support?");
  let workspaceId = String(body.workspaceId || "retrieval-workspace");
  let caseId = String(body.caseId || "retrieval-case");
  let objective = String(body.objective || "Execute a graph-grounded retrieval.");
  const extractionRunId = String(body.extractionRunId || "");

  if (extractionRunId && primitives.length === 0) {
    const run = (await readGraphOpsRun(extractionRunId)) as Record<string, unknown>;
    primitives = Array.isArray(run.primitives) ? (run.primitives as GraphOpsPrimitive[]) : [];
    workspaceId = String(run.workspaceId || workspaceId);
    caseId = String(run.caseId || caseId);
    objective = String(run.objective || objective);
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
      sourceTitle: String(body.sourceTitle || "Retrieval execution source"),
      sourceType: String(body.sourceType || "text"),
    });
    primitives = extraction.primitives;
  }

  ruleEvaluation = ruleEvaluation ?? evaluateNeurosymbolicRules(primitives);
  retrievalPlan = retrievalPlan ?? buildGraphOpsRetrievalPlan({ question, primitives, ruleEvaluation });

  return NextResponse.json(
    executeGraphOpsRetrievalLocally({
      plan: retrievalPlan,
      primitives,
      ruleEvaluation,
    }),
  );
}
