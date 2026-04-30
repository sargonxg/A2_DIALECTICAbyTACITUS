import neo4j from "neo4j-driver";
import { NextResponse } from "next/server";
import { extractGraphOpsPrimitives, sampleText } from "@/lib/graphopsExtraction";
import { stageGraphOpsUploadToDatabricks, triggerDatabricksRun } from "@/lib/graphopsDatabricks";
import { evaluateNeurosymbolicRules } from "@/lib/graphopsRules";

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

async function writeToNeo4j(primitives: Array<Record<string, unknown>>) {
  const uri = process.env.NEO4J_URI;
  const username = process.env.NEO4J_USERNAME ?? process.env.NEO4J_USER;
  const password = process.env.NEO4J_PASSWORD;
  const database = process.env.NEO4J_DATABASE || "neo4j";
  if (!uri || !username || !password) {
    return {
      enabled: false,
      written: 0,
      message: "Neo4j secrets are not configured in this deployment.",
    };
  }

  const driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
  try {
    await driver.executeQuery(
      "CREATE CONSTRAINT tacitus_core_v1_id IF NOT EXISTS FOR (n:TacitusCoreV1) REQUIRE n.id IS UNIQUE",
      {},
      { database },
    );
    for (const primitive of primitives) {
      const label = String(primitive.primitive_type ?? "Primitive").replace(/[^A-Za-z0-9_]/g, "");
      await driver.executeQuery(
        `MERGE (n:TacitusCoreV1:${label} {id: $id})
         SET n += $props, n.updated_at = datetime()`,
        { id: primitive.id, props: primitive },
        { database },
      );
    }

    const relationships = [
      { key: "evidence_span_id", type: "EVIDENCED_BY" },
      { key: "chunk_id", type: "FROM_CHUNK" },
      { key: "document_id", type: "FROM_DOCUMENT" },
      { key: "episode_id", type: "IN_EPISODE" },
      { key: "actor_id", type: "ABOUT_ACTOR" },
      { key: "subject_actor_id", type: "ABOUT_ACTOR" },
      { key: "constrains_actor_id", type: "CONSTRAINS" },
      { key: "extraction_run_id", type: "PRODUCED_BY" },
    ];
    let relationshipCount = 0;
    for (const primitive of primitives) {
      for (const relationship of relationships) {
        const target = primitive[relationship.key];
        if (!target || target === primitive.id) continue;
        await driver.executeQuery(
          `MATCH (a:TacitusCoreV1 {id: $source})
           MATCH (b:TacitusCoreV1 {id: $target})
           MERGE (a)-[r:${relationship.type}]->(b)
           SET r.workspace_id = $workspaceId,
               r.case_id = $caseId,
               r.extraction_run_id = $extractionRunId,
               r.updated_at = datetime()`,
          {
            source: primitive.id,
            target,
            workspaceId: primitive.workspace_id,
            caseId: primitive.case_id,
            extractionRunId: primitive.extraction_run_id,
          },
          { database },
        );
        relationshipCount += 1;
      }
    }

    return {
      enabled: true,
      written: primitives.length,
      relationships: relationshipCount,
      message: "Wrote scoped primitives and provenance relationships to Neo4j.",
    };
  } finally {
    await driver.close();
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
  result.ruleEvaluation = evaluateNeurosymbolicRules(result.primitives);

  if (writeGraph) {
    const write = await writeToNeo4j(result.primitives as Array<Record<string, unknown>>);
    result.graphWrite = { requested: true, ...write };
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
    }
    if (databricksWorkflowKey) {
      databricks.workflow = await triggerDatabricksRun(databricksWorkflowKey);
    }
    result.databricks = databricks;
  }

  return NextResponse.json(result);
}
