import { NextResponse } from "next/server";
import { extractGraphOpsPrimitives, sampleText } from "@/lib/graphopsExtraction";
import {
  stageGraphOpsArtifactToDatabricks,
  stageGraphOpsUploadToDatabricks,
  triggerDatabricksRun,
} from "@/lib/graphopsDatabricks";
import { buildGraphOpsGraphWritePlan, writeGraphOpsPlanToNeo4j } from "@/lib/graphopsGraph";
import { persistGraphOpsRun } from "@/lib/graphopsRuns";
import { evaluateNeurosymbolicRules, type RuleEvaluationResult } from "@/lib/graphopsRules";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function extractPdfText(buffer: Buffer): Promise<string> {
  const { PDFParse } = await import("pdf-parse");
  const parser = new PDFParse({ data: buffer });
  try {
    const parsed = await parser.getText();
    return parsed.text?.trim() ?? "";
  } finally {
    await parser.destroy();
  }
}

export async function POST(request: Request) {
  const contentType = request.headers.get("content-type") ?? "";
  let text = "";
  let sourceTitle = "Pasted text";
  let sourceType = "text";
  let workspaceId = "graphops-workspace";
  let caseId = "graphops-case";
  let objective = "Understand the conflict";
  let ontologyProfile = "human-friction";
  let writeGraph = false;
  let sendToDatabricks = false;
  let databricksWorkflowKey = "";

  if (contentType.includes("multipart/form-data")) {
    const form = await request.formData();
    workspaceId = String(form.get("workspaceId") || workspaceId);
    caseId = String(form.get("caseId") || caseId);
    objective = String(form.get("objective") || objective);
    ontologyProfile = String(form.get("ontologyProfile") || ontologyProfile);
    writeGraph = String(form.get("writeGraph") || "false") === "true";
    sendToDatabricks = String(form.get("sendToDatabricks") || "false") === "true";
    databricksWorkflowKey = String(form.get("databricksWorkflowKey") || "");
    const sample = sampleText(String(form.get("sampleKey") || ""));
    const file = form.get("file");
    text = String(form.get("text") || sample || "");

    if (file instanceof File && file.size > 0) {
      sourceTitle = file.name;
      sourceType = file.type || "file";
      const buffer = Buffer.from(await file.arrayBuffer());
      if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
        text = await extractPdfText(buffer);
      } else {
        text = buffer.toString("utf-8");
      }
    }
  } else {
    const body = await request.json().catch(() => ({}));
    workspaceId = String(body.workspaceId || workspaceId);
    caseId = String(body.caseId || caseId);
    objective = String(body.objective || objective);
    ontologyProfile = String(body.ontologyProfile || ontologyProfile);
    writeGraph = Boolean(body.writeGraph);
    sendToDatabricks = Boolean(body.sendToDatabricks);
    databricksWorkflowKey = String(body.databricksWorkflowKey || "");
    sourceTitle = String(body.sourceTitle || sourceTitle);
    sourceType = String(body.sourceType || sourceType);
    text = String(body.text || sampleText(String(body.sampleKey || "")) || "");
  }

  if (!text.trim()) {
    return NextResponse.json({ error: "Provide text, a TXT/PDF file, or a sampleKey." }, { status: 400 });
  }

  const result = extractGraphOpsPrimitives({
    text: text.slice(0, 120000),
    workspaceId,
    caseId,
    objective,
    ontologyProfile,
    sourceTitle,
    sourceType,
  });
  const ruleEvaluation = evaluateNeurosymbolicRules(result.primitives);
  result.ruleEvaluation = ruleEvaluation as unknown as Record<string, unknown>;

  if (writeGraph) {
    const plan = buildGraphOpsGraphWritePlan({ primitives: result.primitives, ruleEvaluation });
    const write = await writeGraphOpsPlanToNeo4j(plan);
    result.graphWrite = {
      requested: true,
      enabled: write.enabled,
      written: write.written,
      relationships: write.relationships,
      ruleSignalsWritten: ruleEvaluation.signals.length,
      message: write.message,
      plan: plan.summary,
      warnings: write.warnings,
    };
  }
  if (sendToDatabricks || databricksWorkflowKey) {
    const databricks: Record<string, unknown> = {};
    if (sendToDatabricks) {
      databricks.upload = await stageGraphOpsUploadToDatabricks({
        workspaceId,
        caseId,
        extractionRunId: result.extractionRunId,
        sourceTitle,
        sourceType,
        objective,
        ontologyProfile,
        text: text.slice(0, 120000),
        counts: result.counts,
      });
      databricks.ruleEvaluation = await stageGraphOpsArtifactToDatabricks({
        workspaceId,
        caseId,
        artifactType: "rule-evaluations",
        artifactId: result.extractionRunId,
        payload: {
          kind: "tacitus.dialectica.rule_evaluation.v1",
          workspace_id: workspaceId,
          case_id: caseId,
          extraction_run_id: result.extractionRunId,
          ...ruleEvaluation,
        },
      });
    }
    if (databricksWorkflowKey) {
      databricks.workflow = await triggerDatabricksRun(databricksWorkflowKey);
    }
    result.databricks = databricks;
  }

  result.localPersistence = await persistGraphOpsRun({
    result: result as unknown as Record<string, unknown>,
    sourceTitle,
    sourceType,
  });

  return NextResponse.json(result);
}
