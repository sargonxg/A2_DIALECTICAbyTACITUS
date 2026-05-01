import { NextResponse } from "next/server";
import type { GraphOpsExtractionResult, GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { buildGraphOpsPromoStudioRun } from "@/lib/graphopsPromo";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function coerceExtraction(value: unknown): GraphOpsExtractionResult | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<GraphOpsExtractionResult>;
  return candidate.extractionRunId && Array.isArray(candidate.primitives)
    ? (candidate as GraphOpsExtractionResult)
    : undefined;
}

function coerceRuleEvaluation(value: unknown): RuleEvaluationResult | undefined {
  if (!value || typeof value !== "object") return undefined;
  const candidate = value as Partial<RuleEvaluationResult>;
  return candidate.mode === "deterministic_neurosymbolic_rules" && Array.isArray(candidate.signals)
    ? (candidate as RuleEvaluationResult)
    : undefined;
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  try {
    const extraction = coerceExtraction(body.extraction);
    const promo = await buildGraphOpsPromoStudioRun({
      extraction,
      primitives: extraction
        ? undefined
        : Array.isArray(body.primitives)
          ? (body.primitives as GraphOpsPrimitive[])
          : undefined,
      ruleEvaluation: coerceRuleEvaluation(body.ruleEvaluation),
      text: typeof body.text === "string" ? body.text : undefined,
      sampleKey: typeof body.sampleKey === "string" ? body.sampleKey : undefined,
      workspaceId: typeof body.workspaceId === "string" ? body.workspaceId : undefined,
      caseId: typeof body.caseId === "string" ? body.caseId : undefined,
      objective: typeof body.objective === "string" ? body.objective : undefined,
      ontologyProfile: typeof body.ontologyProfile === "string" ? body.ontologyProfile : undefined,
      sourceTitle: typeof body.sourceTitle === "string" ? body.sourceTitle : undefined,
      sourceType: typeof body.sourceType === "string" ? body.sourceType : undefined,
      question: typeof body.question === "string" ? body.question : undefined,
      answerDraft: typeof body.answerDraft === "string" ? body.answerDraft : undefined,
      command: typeof body.command === "string" ? body.command : undefined,
    });
    return NextResponse.json(promo);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Could not build promo studio run." },
      { status: 400 },
    );
  }
}
