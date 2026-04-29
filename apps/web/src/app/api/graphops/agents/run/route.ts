import { NextResponse } from "next/server";
import { triggerDatabricksRun } from "@/lib/graphopsDatabricks";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const AGENTS = {
  "source-scout": {
    name: "Source Scout",
    action: "Stages source-pack ingestion work and can launch the open-book extraction demo.",
    workflowKey: "book-demo",
    next: ["/api/graphops/ingest", "/api/graphops/databricks/tables"],
  },
  "ontology-builder": {
    name: "Ontology Builder",
    action: "Builds an objective-specific ontology profile before extraction.",
    next: ["/api/graphops/ingest", "/api/graphops/manifest"],
  },
  "claim-verifier": {
    name: "Claim Verifier",
    action: "Prioritizes low-confidence and weak-evidence graph items for review.",
    workflowKey: "complex-demo",
    next: ["/api/graphops/databricks/tables", "/api/graphops/query"],
  },
  "temporal-analyst": {
    name: "Temporal Analyst",
    action: "Runs temporal and profile-quality analysis over the case workspace.",
    workflowKey: "complex-demo",
    next: ["/api/graphops/databricks/tables", "/api/graphops/query"],
  },
  "graphrag-planner": {
    name: "GraphRAG Planner",
    action: "Converts a hard question into allowlisted graph traversals plus provenance requirements.",
    next: ["/api/graphops/query"],
  },
  "benchmark-judge": {
    name: "Benchmark Judge",
    action: "Launches the baseline-vs-DIALECTICA benchmark workflow.",
    workflowKey: "benchmark",
    next: ["/api/graphops/databricks/jobs", "/api/graphops/databricks/tables"],
  },
} as const;

function agentKey(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const key = agentKey(String(body.agent ?? ""));
  const execute = Boolean(body.execute);
  const workspaceId = String(body.workspaceId ?? "graphops-workspace");
  const caseId = String(body.caseId ?? "graphops-case");
  const objective = String(body.objective ?? "Understand the conflict");
  const agent = AGENTS[key as keyof typeof AGENTS];

  if (!agent) {
    return NextResponse.json({ error: "Unknown GraphOps agent." }, { status: 400 });
  }

  const plan = {
    agent: agent.name,
    workspace_id: workspaceId,
    case_id: caseId,
    objective,
    mode: execute ? "execute_allowlisted_actions" : "plan_only",
    action: agent.action,
    guardrails: [
      "No browser-side secrets.",
      "Only allowlisted Databricks jobs may be triggered.",
      "Neo4j writes require server-side rotated credentials.",
      "Every graph fact must retain source provenance.",
    ],
    next_endpoints: agent.next,
  };

  const workflow = execute && "workflowKey" in agent ? await triggerDatabricksRun(agent.workflowKey) : null;
  return NextResponse.json({ plan, workflow });
}
