import { NextResponse } from "next/server";
import { persistGraphOpsArtifact } from "@/lib/graphopsArtifacts";
import { buildGraphOpsDemoReadyRun } from "@/lib/graphopsDemo";
import type { GraphOpsExtractionResult, GraphOpsPrimitive } from "@/lib/graphopsExtraction";
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
    const demo = buildGraphOpsDemoReadyRun({
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
    });
    let persistence:
      | Awaited<ReturnType<typeof persistGraphOpsArtifact>>
      | { enabled: false; saved: false; message: string }
      | { enabled: true; saved: false; message: string; error: string };
    if (body.persist === false) {
      persistence = { enabled: false, saved: false, message: "Persistence disabled by request." };
    } else {
      try {
        persistence = await persistGraphOpsArtifact({
          artifactType: "demo-ready-runs",
          artifactId: demo.demoId,
          payload: demo as unknown as Record<string, unknown>,
        });
      } catch (error) {
        persistence = {
          enabled: true,
          saved: false,
          message: "Demo run succeeded, but local artifact persistence failed.",
          error: error instanceof Error ? error.message : "Unknown persistence error.",
        };
      }
    }
    return NextResponse.json({ ...demo, persistence });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Could not build demo-ready run." },
      { status: 400 },
    );
  }
}
