import { NextResponse } from "next/server";
import { extractGraphOpsPrimitives, sampleText, type GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import { evaluateNeurosymbolicRules } from "@/lib/graphopsRules";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const primitives = Array.isArray(body.primitives) ? body.primitives as GraphOpsPrimitive[] : null;
  if (primitives && primitives.length > 0) {
    return NextResponse.json(evaluateNeurosymbolicRules(primitives));
  }

  const text = String(body.text || sampleText(String(body.sampleKey || "romeo-juliet-conflict")) || "");
  if (!text.trim()) {
    return NextResponse.json({ error: "Provide primitives, text, or sampleKey." }, { status: 400 });
  }

  const extraction = extractGraphOpsPrimitives({
    text: text.slice(0, 120000),
    workspaceId: String(body.workspaceId || "books-romeo-juliet"),
    caseId: String(body.caseId || "romeo-juliet-conflict"),
    objective: String(body.objective || "Understand the conflict with a conflict-resolution lens."),
    ontologyProfile: String(body.ontologyProfile || "literary-conflict"),
    sourceTitle: String(body.sourceTitle || "Rule evaluation sample"),
    sourceType: String(body.sourceType || "text"),
  });

  return NextResponse.json({
    extraction: {
      extractionRunId: extraction.extractionRunId,
      counts: extraction.counts,
      graphPreview: extraction.graphPreview,
    },
    ...evaluateNeurosymbolicRules(extraction.primitives),
  });
}
