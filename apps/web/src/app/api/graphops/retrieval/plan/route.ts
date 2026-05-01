import { NextResponse } from "next/server";
import { extractGraphOpsPrimitives, sampleText, type GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { readGraphOpsRun } from "@/lib/graphopsRuns";
import { evaluateNeurosymbolicRules, type RuleEvaluationResult } from "@/lib/graphopsRules";
import { buildGraphOpsRetrievalPlan } from "@/lib/graphopsRetrieval";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function coerceRuleEvaluation(value: unknown): RuleEvaluationResult | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<RuleEvaluationResult>;
  return candidate.mode === "deterministic_neurosymbolic_rules" && Array.isArray(candidate.signals)
    ? (candidate as RuleEvaluationResult)
    : undefined;
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  let primitives = Array.isArray(body.primitives) ? (body.primitives as GraphOpsPrimitive[]) : [];
  let ruleEvaluation = coerceRuleEvaluation(body.ruleEvaluation);
  const question = String(body.question || "What does the graph-grounded evidence support?");

  if (body.extractionRunId && primitives.length === 0) {
    const run = (await readGraphOpsRun(String(body.extractionRunId))) as Record<string, unknown>;
    primitives = Array.isArray(run.primitives) ? (run.primitives as GraphOpsPrimitive[]) : [];
    ruleEvaluation = coerceRuleEvaluation(run.ruleEvaluation) ?? ruleEvaluation;
  }

  if (primitives.length === 0 && (body.text || body.sampleKey)) {
    const text = String(body.text || sampleText(String(body.sampleKey || "")) || "");
    if (text.trim()) {
      const extraction = extractGraphOpsPrimitives({
        text: text.slice(0, 120000),
        workspaceId: String(body.workspaceId || "retrieval-workspace"),
        caseId: String(body.caseId || "retrieval-case"),
        objective: String(body.objective || "Plan a graph-grounded retrieval."),
        ontologyProfile: String(body.ontologyProfile || "human-friction"),
        sourceTitle: String(body.sourceTitle || "Retrieval planning source"),
        sourceType: String(body.sourceType || "text"),
      });
      primitives = extraction.primitives;
      ruleEvaluation = evaluateNeurosymbolicRules(primitives);
    }
  }

  return NextResponse.json(
    buildGraphOpsRetrievalPlan({
      question,
      primitives,
      ruleEvaluation: ruleEvaluation ?? (primitives.length > 0 ? evaluateNeurosymbolicRules(primitives) : undefined),
    }),
  );
}
