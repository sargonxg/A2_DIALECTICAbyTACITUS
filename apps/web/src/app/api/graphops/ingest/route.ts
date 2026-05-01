import neo4j, { type Driver } from "neo4j-driver";
import { NextResponse } from "next/server";
import { extractGraphOpsPrimitives, sampleText } from "@/lib/graphopsExtraction";
import {
  stageGraphOpsArtifactToDatabricks,
  stageGraphOpsUploadToDatabricks,
  triggerDatabricksRun,
} from "@/lib/graphopsDatabricks";
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

function safeLabel(value: unknown) {
  const label = String(value ?? "Primitive").replace(/[^A-Za-z0-9_]/g, "");
  return label || "Primitive";
}

function safeIdPart(value: string) {
  return value.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 96) || "item";
}

function baseGraphProps(input: {
  id: string;
  primitiveType: string;
  workspaceId: string;
  caseId: string;
  extractionRunId: string;
  extra?: Record<string, unknown>;
}) {
  return {
    id: input.id,
    primitive_type: input.primitiveType,
    workspace_id: input.workspaceId,
    case_id: input.caseId,
    extraction_run_id: input.extractionRunId,
    ontology_version: "tacitus_core_v1",
    observed_at: new Date().toISOString(),
    ...(input.extra ?? {}),
  };
}

async function writeRuleEvaluationToNeo4j(
  driver: Driver,
  database: string,
  ruleEvaluation: RuleEvaluationResult,
  context: {
    workspaceId: string;
    caseId: string;
    extractionRunId: string;
  },
) {
  const statements = [
    "CREATE CONSTRAINT tacitus_rule_signal_id IF NOT EXISTS FOR (n:RuleSignal) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT tacitus_rule_fire_id IF NOT EXISTS FOR (n:RuleFire) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT tacitus_answer_constraint_id IF NOT EXISTS FOR (n:AnswerConstraint) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT tacitus_benchmark_target_id IF NOT EXISTS FOR (n:BenchmarkTarget) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT tacitus_review_decision_id IF NOT EXISTS FOR (n:ReviewDecision) REQUIRE n.id IS UNIQUE",
  ];
  for (const statement of statements) {
    await driver.executeQuery(statement, {}, { database });
  }

  let written = 0;
  let relationships = 0;
  for (const signal of ruleEvaluation.signals) {
    const signalProps = baseGraphProps({
      id: signal.id,
      primitiveType: "RuleSignal",
      ...context,
      extra: signal,
    });
    await driver.executeQuery(
      `MERGE (s:TacitusCoreV1:RuleSignal {id: $id})
       SET s += $props, s.updated_at = datetime()`,
      { id: signal.id, props: signalProps },
      { database },
    );
    written += 1;

    const fireId = `fire_${signal.id}`;
    const fireProps = baseGraphProps({
      id: fireId,
      primitiveType: "RuleFire",
      ...context,
      extra: {
        rule_id: signal.rule_id,
        rule_name: signal.rule_name,
        severity: signal.severity,
        status: signal.status,
        fired_at: new Date().toISOString(),
      },
    });
    await driver.executeQuery(
      `MERGE (f:TacitusCoreV1:RuleFire {id: $id})
       SET f += $props, f.updated_at = datetime()
       WITH f
       MATCH (s:TacitusCoreV1:RuleSignal {id: $signalId})
       MERGE (f)-[r:FIRED_SIGNAL]->(s)
       SET r.workspace_id = $workspaceId,
           r.case_id = $caseId,
           r.extraction_run_id = $extractionRunId,
           r.updated_at = datetime()
       WITH f
       OPTIONAL MATCH (run:TacitusCoreV1:ExtractionRun {id: $extractionRunId})
       FOREACH (_ IN CASE WHEN run IS NULL THEN [] ELSE [1] END |
         MERGE (f)-[:PRODUCED_BY]->(run)
       )`,
      {
        id: fireId,
        props: fireProps,
        signalId: signal.id,
        workspaceId: context.workspaceId,
        caseId: context.caseId,
        extractionRunId: context.extractionRunId,
      },
      { database },
    );
    written += 1;
    relationships += 1;

    for (const evidenceId of signal.evidence_ids) {
      await driver.executeQuery(
        `MATCH (s:TacitusCoreV1:RuleSignal {id: $signalId})
         MATCH (e:TacitusCoreV1 {id: $evidenceId})
         MERGE (s)-[r:SUPPORTED_BY]->(e)
         SET r.workspace_id = $workspaceId,
             r.case_id = $caseId,
             r.extraction_run_id = $extractionRunId,
             r.updated_at = datetime()`,
        {
          signalId: signal.id,
          evidenceId,
          workspaceId: context.workspaceId,
          caseId: context.caseId,
          extractionRunId: context.extractionRunId,
        },
        { database },
      );
      relationships += 1;
    }

    for (const affectedId of signal.affected_ids) {
      await driver.executeQuery(
        `MATCH (s:TacitusCoreV1:RuleSignal {id: $signalId})
         MATCH (a:TacitusCoreV1 {id: $affectedId})
         MERGE (s)-[r:AFFECTS]->(a)
         SET r.workspace_id = $workspaceId,
             r.case_id = $caseId,
             r.extraction_run_id = $extractionRunId,
             r.updated_at = datetime()`,
        {
          signalId: signal.id,
          affectedId,
          workspaceId: context.workspaceId,
          caseId: context.caseId,
          extractionRunId: context.extractionRunId,
        },
        { database },
      );
      relationships += 1;
    }

    if (signal.severity !== "info") {
      const reviewId = `review_${signal.id}`;
      const reviewProps = baseGraphProps({
        id: reviewId,
        primitiveType: "ReviewDecision",
        ...context,
        extra: {
          rule_signal_id: signal.id,
          status: "pending_review",
          severity: signal.severity,
          recommended_action: signal.recommended_action,
        },
      });
      await driver.executeQuery(
        `MERGE (d:TacitusCoreV1:ReviewDecision {id: $id})
         SET d += $props, d.updated_at = datetime()
         WITH d
         MATCH (s:TacitusCoreV1:RuleSignal {id: $signalId})
         MERGE (d)-[r:REVIEWS_SIGNAL]->(s)
         SET r.workspace_id = $workspaceId,
             r.case_id = $caseId,
             r.extraction_run_id = $extractionRunId,
             r.updated_at = datetime()`,
        {
          id: reviewId,
          props: reviewProps,
          signalId: signal.id,
          workspaceId: context.workspaceId,
          caseId: context.caseId,
          extractionRunId: context.extractionRunId,
        },
        { database },
      );
      written += 1;
      relationships += 1;
    }
  }

  for (const [index, text] of ruleEvaluation.answerConstraints.entries()) {
    const id = `${context.extractionRunId}_answer_constraint_${index + 1}`;
    await driver.executeQuery(
      `MERGE (c:TacitusCoreV1:AnswerConstraint {id: $id})
       SET c += $props, c.updated_at = datetime()
       WITH c
       OPTIONAL MATCH (run:TacitusCoreV1:ExtractionRun {id: $extractionRunId})
       FOREACH (_ IN CASE WHEN run IS NULL THEN [] ELSE [1] END |
         MERGE (c)-[:CONSTRAINS_ANSWER_FOR]->(run)
       )`,
      {
        id,
        props: baseGraphProps({
          id,
          primitiveType: "AnswerConstraint",
          ...context,
          extra: { text, position: index + 1 },
        }),
        extractionRunId: context.extractionRunId,
      },
      { database },
    );
    written += 1;
    relationships += 1;
  }

  for (const target of ruleEvaluation.benchmarkTargets) {
    const id = `${context.extractionRunId}_benchmark_${safeIdPart(target)}`;
    await driver.executeQuery(
      `MERGE (b:TacitusCoreV1:BenchmarkTarget {id: $id})
       SET b += $props, b.updated_at = datetime()
       WITH b
       OPTIONAL MATCH (run:TacitusCoreV1:ExtractionRun {id: $extractionRunId})
       FOREACH (_ IN CASE WHEN run IS NULL THEN [] ELSE [1] END |
         MERGE (b)-[:BENCHMARKS_RUN]->(run)
       )`,
      {
        id,
        props: baseGraphProps({
          id,
          primitiveType: "BenchmarkTarget",
          ...context,
          extra: { target },
        }),
        extractionRunId: context.extractionRunId,
      },
      { database },
    );
    written += 1;
    relationships += 1;
  }

  return { written, relationships };
}

async function writeToNeo4j(
  primitives: Array<Record<string, unknown>>,
  ruleEvaluation?: RuleEvaluationResult,
) {
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
      const label = safeLabel(primitive.primitive_type);
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

    const extractionRunId = String(primitives[0]?.extraction_run_id ?? "");
    const workspaceId = String(primitives[0]?.workspace_id ?? "");
    const caseId = String(primitives[0]?.case_id ?? "");
    const ruleWrite =
      ruleEvaluation && extractionRunId && workspaceId && caseId
        ? await writeRuleEvaluationToNeo4j(driver, database, ruleEvaluation, {
            workspaceId,
            caseId,
            extractionRunId,
          })
        : { written: 0, relationships: 0 };

    return {
      enabled: true,
      written: primitives.length + ruleWrite.written,
      relationships: relationshipCount + ruleWrite.relationships,
      ruleSignalsWritten: ruleEvaluation?.signals.length ?? 0,
      message:
        ruleWrite.written > 0
          ? "Wrote scoped primitives, rule signals, answer constraints, benchmark targets, and provenance relationships to Neo4j."
          : "Wrote scoped primitives and provenance relationships to Neo4j.",
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
  const ruleEvaluation = evaluateNeurosymbolicRules(result.primitives);
  result.ruleEvaluation = ruleEvaluation as unknown as Record<string, unknown>;

  if (writeGraph) {
    const write = await writeToNeo4j(result.primitives as Array<Record<string, unknown>>, ruleEvaluation);
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
