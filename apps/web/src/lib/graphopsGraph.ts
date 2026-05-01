import neo4j from "neo4j-driver";
import type { GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import type { GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

export type GraphOpsGraphNode = {
  id: string;
  labels: string[];
  primitiveType: string;
  properties: Record<string, unknown>;
};

export type GraphOpsGraphEdge = {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
};

export type GraphOpsGraphWritePlan = {
  kind: "tacitus.dialectica.graph_write_plan.v1";
  createdAt: string;
  workspaceId: string;
  caseId: string;
  extractionRunId: string;
  schemaStatements: string[];
  nodes: GraphOpsGraphNode[];
  edges: GraphOpsGraphEdge[];
  warnings: string[];
  summary: {
    nodes: number;
    edges: number;
    primitiveNodes: number;
    ruleNodes: number;
    benchmarkNodes: number;
    reviewNodes: number;
  };
};

export type GraphOpsGraphWriteResult = {
  enabled: boolean;
  requested: boolean;
  written: number;
  relationships: number;
  message: string;
  database?: string;
  warnings?: string[];
};

export type GraphOpsGraphStatus = {
  kind: "tacitus.dialectica.graph_status.v1";
  checkedAt: string;
  configured: boolean;
  connected: boolean;
  database: string;
  workspaceId?: string;
  caseId?: string;
  message: string;
  counts: {
    nodes: number;
    relationships: number;
    byPrimitiveType: Record<string, number>;
    ruleSignals: number;
    reviewDecisions: number;
    benchmarkRuns: number;
  };
  latestRuns: Array<{ extractionRunId: string; observedAt: string | null; nodes: number }>;
  error?: string;
};

const RELATIONSHIP_KEYS: Array<{ key: string; type: string }> = [
  { key: "evidence_span_id", type: "GROUNDED_IN" },
  { key: "chunk_id", type: "QUOTES" },
  { key: "document_id", type: "FROM_DOCUMENT" },
  { key: "episode_id", type: "IN_EPISODE" },
  { key: "actor_id", type: "ABOUT_ACTOR" },
  { key: "subject_actor_id", type: "MADE_BY" },
  { key: "constrains_actor_id", type: "CONSTRAINS" },
  { key: "extraction_run_id", type: "PRODUCED_BY" },
];

const SCHEMA_STATEMENTS = [
  "CREATE CONSTRAINT tacitus_core_v1_id IF NOT EXISTS FOR (n:TacitusCoreV1) REQUIRE n.id IS UNIQUE",
  "CREATE INDEX tacitus_core_workspace IF NOT EXISTS FOR (n:TacitusCoreV1) ON (n.workspace_id)",
  "CREATE INDEX tacitus_core_case IF NOT EXISTS FOR (n:TacitusCoreV1) ON (n.case_id)",
  "CREATE INDEX tacitus_core_extraction_run IF NOT EXISTS FOR (n:TacitusCoreV1) ON (n.extraction_run_id)",
  "CREATE INDEX tacitus_core_primitive_type IF NOT EXISTS FOR (n:TacitusCoreV1) ON (n.primitive_type)",
  "CREATE INDEX tacitus_core_review_status IF NOT EXISTS FOR (n:TacitusCoreV1) ON (n.review_status)",
  "CREATE INDEX tacitus_core_observed_at IF NOT EXISTS FOR (n:TacitusCoreV1) ON (n.observed_at)",
  "CREATE FULLTEXT INDEX tacitus_claim_text IF NOT EXISTS FOR (n:Claim) ON EACH [n.text, n.provenance_span]",
  "CREATE FULLTEXT INDEX tacitus_chunk_text IF NOT EXISTS FOR (n:SourceChunk) ON EACH [n.text]",
];

export function neo4jConfigured() {
  return Boolean(
    process.env.NEO4J_URI &&
      (process.env.NEO4J_USERNAME || process.env.NEO4J_USER) &&
      process.env.NEO4J_PASSWORD,
  );
}

export function safeGraphLabel(value: unknown) {
  const label = String(value ?? "Primitive").replace(/[^A-Za-z0-9_]/g, "");
  return label || "Primitive";
}

export function safeRelationshipType(value: unknown) {
  const type = String(value ?? "RELATED_TO")
    .replace(/[^A-Za-z0-9_]/g, "_")
    .toUpperCase();
  return type || "RELATED_TO";
}

function safeIdPart(value: unknown) {
  return String(value ?? "item")
    .replace(/[^A-Za-z0-9_.-]/g, "_")
    .slice(0, 96) || "item";
}

function sanitizePropertyValue(value: unknown): unknown {
  if (value === undefined || value === null) return undefined;
  if (value instanceof Date) return value.toISOString();
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return value;
  if (Array.isArray(value)) {
    if (value.every((item) => ["string", "number", "boolean"].includes(typeof item))) return value;
    return JSON.stringify(value);
  }
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function sanitizeProperties(input: Record<string, unknown>) {
  return Object.fromEntries(
    Object.entries(input)
      .map(([key, value]) => [key, sanitizePropertyValue(value)] as const)
      .filter((entry): entry is readonly [string, unknown] => entry[1] !== undefined),
  );
}

function baseProps(input: {
  id: string;
  primitiveType: string;
  workspaceId: string;
  caseId: string;
  extractionRunId: string;
  extra?: Record<string, unknown>;
}) {
  return sanitizeProperties({
    id: input.id,
    primitive_type: input.primitiveType,
    workspace_id: input.workspaceId,
    case_id: input.caseId,
    extraction_run_id: input.extractionRunId,
    ontology_version: "tacitus_core_v1",
    observed_at: new Date().toISOString(),
    ...(input.extra ?? {}),
  });
}

function node(input: {
  id: string;
  primitiveType: string;
  workspaceId: string;
  caseId: string;
  extractionRunId: string;
  extra?: Record<string, unknown>;
}): GraphOpsGraphNode {
  return {
    id: input.id,
    labels: ["TacitusCoreV1", safeGraphLabel(input.primitiveType)],
    primitiveType: input.primitiveType,
    properties: baseProps(input),
  };
}

function edge(input: {
  source: string;
  target: string;
  type: string;
  workspaceId: string;
  caseId: string;
  extractionRunId: string;
  extra?: Record<string, unknown>;
}): GraphOpsGraphEdge {
  const type = safeRelationshipType(input.type);
  const id = `${safeIdPart(input.source)}_${type}_${safeIdPart(input.target)}`.slice(0, 220);
  return {
    id,
    source: input.source,
    target: input.target,
    type,
    properties: sanitizeProperties({
      id,
      workspace_id: input.workspaceId,
      case_id: input.caseId,
      extraction_run_id: input.extractionRunId,
      updated_at_iso: new Date().toISOString(),
      ...(input.extra ?? {}),
    }),
  };
}

export function buildGraphOpsGraphWritePlan(input: {
  primitives: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
  benchmark?: GraphOpsBenchmarkResult;
}): GraphOpsGraphWritePlan {
  const first = input.primitives[0];
  const workspaceId = String(first?.workspace_id ?? "graphops-workspace");
  const caseId = String(first?.case_id ?? "graphops-case");
  const extractionRunId = String(first?.extraction_run_id ?? first?.id ?? `run_${Date.now()}`);
  const nodes: GraphOpsGraphNode[] = [];
  const edges: GraphOpsGraphEdge[] = [];
  const warnings: string[] = [];
  const nodeIds = new Set<string>();

  for (const primitive of input.primitives) {
    const primitiveType = safeGraphLabel(primitive.primitive_type);
    nodes.push({
      id: primitive.id,
      labels: ["TacitusCoreV1", primitiveType],
      primitiveType,
      properties: sanitizeProperties(primitive),
    });
    nodeIds.add(primitive.id);
  }

  for (const primitive of input.primitives) {
    for (const relationship of RELATIONSHIP_KEYS) {
      const target = primitive[relationship.key];
      if (typeof target !== "string" || !target || target === primitive.id) continue;
      if (!nodeIds.has(target)) {
        warnings.push(`Skipped ${relationship.type} from ${primitive.id} to missing node ${target}.`);
        continue;
      }
      edges.push(
        edge({
          source: primitive.id,
          target,
          type: relationship.type,
          workspaceId,
          caseId,
          extractionRunId,
          extra: { source_key: relationship.key, confidence: primitive.confidence },
        }),
      );
    }
  }

  for (const signal of input.ruleEvaluation?.signals ?? []) {
    nodes.push(
      node({
        id: signal.id,
        primitiveType: "RuleSignal",
        workspaceId,
        caseId,
        extractionRunId,
        extra: signal as unknown as Record<string, unknown>,
      }),
    );
    nodeIds.add(signal.id);

    const fireId = `fire_${signal.id}`;
    nodes.push(
      node({
        id: fireId,
        primitiveType: "RuleFire",
        workspaceId,
        caseId,
        extractionRunId,
        extra: {
          rule_id: signal.rule_id,
          rule_name: signal.rule_name,
          severity: signal.severity,
          status: signal.status,
          fired_at: new Date().toISOString(),
        },
      }),
    );
    nodeIds.add(fireId);
    edges.push(edge({ source: fireId, target: signal.id, type: "FIRED_SIGNAL", workspaceId, caseId, extractionRunId }));
    if (nodeIds.has(extractionRunId)) {
      edges.push(edge({ source: fireId, target: extractionRunId, type: "PRODUCED_BY", workspaceId, caseId, extractionRunId }));
    }

    for (const evidenceId of signal.evidence_ids) {
      if (nodeIds.has(evidenceId)) {
        edges.push(edge({ source: signal.id, target: evidenceId, type: "SUPPORTED_BY", workspaceId, caseId, extractionRunId }));
      }
    }
    for (const affectedId of signal.affected_ids) {
      if (nodeIds.has(affectedId)) {
        edges.push(edge({ source: signal.id, target: affectedId, type: "AFFECTS", workspaceId, caseId, extractionRunId }));
      }
    }
    if (signal.severity !== "info") {
      const reviewId = `review_${signal.id}`;
      nodes.push(
        node({
          id: reviewId,
          primitiveType: "ReviewDecision",
          workspaceId,
          caseId,
          extractionRunId,
          extra: {
            rule_signal_id: signal.id,
            review_status: "pending",
            severity: signal.severity,
            recommended_action: signal.recommended_action,
          },
        }),
      );
      nodeIds.add(reviewId);
      edges.push(edge({ source: reviewId, target: signal.id, type: "REVIEWS_SIGNAL", workspaceId, caseId, extractionRunId }));
    }
  }

  for (const [index, text] of (input.ruleEvaluation?.answerConstraints ?? []).entries()) {
    const constraintId = `${extractionRunId}_answer_constraint_${index + 1}`;
    nodes.push(
      node({
        id: constraintId,
        primitiveType: "AnswerConstraint",
        workspaceId,
        caseId,
        extractionRunId,
        extra: { text, position: index + 1 },
      }),
    );
    if (nodeIds.has(extractionRunId)) {
      edges.push(edge({ source: constraintId, target: extractionRunId, type: "CONSTRAINS_ANSWER_FOR", workspaceId, caseId, extractionRunId }));
    }
  }

  for (const target of input.ruleEvaluation?.benchmarkTargets ?? []) {
    const benchmarkId = `${extractionRunId}_benchmark_${safeIdPart(target)}`;
    nodes.push(
      node({
        id: benchmarkId,
        primitiveType: "BenchmarkTarget",
        workspaceId,
        caseId,
        extractionRunId,
        extra: { target },
      }),
    );
    if (nodeIds.has(extractionRunId)) {
      edges.push(edge({ source: benchmarkId, target: extractionRunId, type: "BENCHMARKS_RUN", workspaceId, caseId, extractionRunId }));
    }
  }

  if (input.benchmark) {
    const benchmarkRunId = input.benchmark.benchmarkId;
    nodes.push(
      node({
        id: benchmarkRunId,
        primitiveType: "BenchmarkRun",
        workspaceId,
        caseId,
        extractionRunId,
        extra: {
          mode: input.benchmark.mode,
          overall: input.benchmark.scores.overall,
          evidence_grounding: input.benchmark.scores.evidenceGrounding,
          causal_discipline: input.benchmark.scores.causalDiscipline,
          rule_compliance: input.benchmark.scores.ruleCompliance,
          created_at: input.benchmark.createdAt,
        },
      }),
    );
    if (nodeIds.has(extractionRunId)) {
      edges.push(edge({ source: benchmarkRunId, target: extractionRunId, type: "EVALUATES_RUN", workspaceId, caseId, extractionRunId }));
    }
  }

  const uniqueNodes = [...new Map(nodes.map((item) => [item.id, item])).values()];
  const uniqueEdges = [...new Map(edges.map((item) => [item.id, item])).values()];

  return {
    kind: "tacitus.dialectica.graph_write_plan.v1",
    createdAt: new Date().toISOString(),
    workspaceId,
    caseId,
    extractionRunId,
    schemaStatements: SCHEMA_STATEMENTS,
    nodes: uniqueNodes,
    edges: uniqueEdges,
    warnings: [...new Set(warnings)].slice(0, 25),
    summary: {
      nodes: uniqueNodes.length,
      edges: uniqueEdges.length,
      primitiveNodes: input.primitives.length,
      ruleNodes: uniqueNodes.filter((item) => ["RuleSignal", "RuleFire", "AnswerConstraint"].includes(item.primitiveType)).length,
      benchmarkNodes: uniqueNodes.filter((item) => ["BenchmarkRun", "BenchmarkTarget"].includes(item.primitiveType)).length,
      reviewNodes: uniqueNodes.filter((item) => item.primitiveType === "ReviewDecision").length,
    },
  };
}

export async function writeGraphOpsPlanToNeo4j(plan: GraphOpsGraphWritePlan): Promise<GraphOpsGraphWriteResult> {
  const uri = process.env.NEO4J_URI;
  const username = process.env.NEO4J_USERNAME ?? process.env.NEO4J_USER;
  const password = process.env.NEO4J_PASSWORD;
  const database = process.env.NEO4J_DATABASE || "neo4j";
  if (!uri || !username || !password) {
    return {
      enabled: false,
      requested: true,
      written: 0,
      relationships: 0,
      warnings: plan.warnings,
      message: "Neo4j secrets are not configured in this deployment.",
    };
  }

  const driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
  try {
    for (const statement of plan.schemaStatements) {
      try {
        await driver.executeQuery(statement, {}, { database });
      } catch {
        if (!statement.includes("FULLTEXT INDEX")) throw new Error(`Neo4j schema statement failed: ${statement}`);
      }
    }

    for (const item of plan.nodes) {
      const labels = item.labels.map(safeGraphLabel).join(":");
      await driver.executeQuery(
        `MERGE (n:${labels} {id: $id})
         SET n += $props, n.updated_at = datetime()`,
        { id: item.id, props: item.properties },
        { database },
      );
    }

    let relationships = 0;
    for (const item of plan.edges) {
      const type = safeRelationshipType(item.type);
      await driver.executeQuery(
        `MATCH (s:TacitusCoreV1 {id: $source})
         MATCH (t:TacitusCoreV1 {id: $target})
         MERGE (s)-[r:${type} {id: $id}]->(t)
         SET r += $props, r.updated_at = datetime()`,
        {
          id: item.id,
          source: item.source,
          target: item.target,
          props: item.properties,
        },
        { database },
      );
      relationships += 1;
    }

    return {
      enabled: true,
      requested: true,
      written: plan.nodes.length,
      relationships,
      database,
      warnings: plan.warnings,
      message: "Wrote graph primitives, provenance edges, rule artifacts, review items, and benchmark artifacts to Neo4j.",
    };
  } finally {
    await driver.close();
  }
}

export async function getGraphOpsGraphStatus(input: {
  workspaceId?: string;
  caseId?: string;
}): Promise<GraphOpsGraphStatus> {
  const database = process.env.NEO4J_DATABASE || "neo4j";
  const base = {
    kind: "tacitus.dialectica.graph_status.v1" as const,
    checkedAt: new Date().toISOString(),
    configured: neo4jConfigured(),
    connected: false,
    database,
    workspaceId: input.workspaceId,
    caseId: input.caseId,
    counts: {
      nodes: 0,
      relationships: 0,
      byPrimitiveType: {},
      ruleSignals: 0,
      reviewDecisions: 0,
      benchmarkRuns: 0,
    },
    latestRuns: [],
  };

  const uri = process.env.NEO4J_URI;
  const username = process.env.NEO4J_USERNAME ?? process.env.NEO4J_USER;
  const password = process.env.NEO4J_PASSWORD;
  if (!uri || !username || !password) {
    return {
      ...base,
      message: "Neo4j secrets are not configured in this deployment.",
    };
  }

  const where = [
    input.workspaceId ? "n.workspace_id = $workspaceId" : "",
    input.caseId ? "n.case_id = $caseId" : "",
  ].filter(Boolean);
  const whereClause = where.length > 0 ? `WHERE ${where.join(" AND ")}` : "";
  const params = {
    workspaceId: input.workspaceId,
    caseId: input.caseId,
  };
  const driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
  try {
    const nodeRecords = await driver.executeQuery(
      `MATCH (n:TacitusCoreV1)
       ${whereClause}
       RETURN coalesce(n.primitive_type, 'Unknown') AS primitiveType, count(n) AS count`,
      params,
      { database },
    );
    const byPrimitiveType: Record<string, number> = {};
    for (const record of nodeRecords.records) {
      const count = record.get("count");
      byPrimitiveType[String(record.get("primitiveType"))] = neo4j.isInt(count) ? count.toNumber() : Number(count);
    }
    const relRecords = await driver.executeQuery(
      `MATCH (n:TacitusCoreV1)-[r]->(m:TacitusCoreV1)
       ${whereClause}
       RETURN count(r) AS count`,
      params,
      { database },
    );
    const relCount = relRecords.records[0]?.get("count");
    const latest = await driver.executeQuery(
      `MATCH (n:TacitusCoreV1)
       ${whereClause}
       WHERE n.extraction_run_id IS NOT NULL
       RETURN n.extraction_run_id AS extractionRunId, max(n.observed_at) AS observedAt, count(n) AS nodes
       ORDER BY observedAt DESC
       LIMIT 8`,
      params,
      { database },
    );

    return {
      ...base,
      connected: true,
      message: "Connected to Neo4j and counted DIALECTICA graph memory.",
      counts: {
        nodes: Object.values(byPrimitiveType).reduce((sum, count) => sum + count, 0),
        relationships: neo4j.isInt(relCount) ? relCount.toNumber() : Number(relCount ?? 0),
        byPrimitiveType,
        ruleSignals: byPrimitiveType.RuleSignal ?? 0,
        reviewDecisions: byPrimitiveType.ReviewDecision ?? 0,
        benchmarkRuns: byPrimitiveType.BenchmarkRun ?? 0,
      },
      latestRuns: latest.records.map((record) => {
        const nodes = record.get("nodes");
        return {
          extractionRunId: String(record.get("extractionRunId")),
          observedAt: record.get("observedAt") ? String(record.get("observedAt")) : null,
          nodes: neo4j.isInt(nodes) ? nodes.toNumber() : Number(nodes ?? 0),
        };
      }),
    };
  } catch (error) {
    return {
      ...base,
      message: "Neo4j status check failed.",
      error: error instanceof Error ? error.message : "Unknown Neo4j status error.",
    };
  } finally {
    await driver.close();
  }
}
