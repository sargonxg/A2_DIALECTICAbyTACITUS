import neo4j from "neo4j-driver";
import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function checkNeo4j() {
  const uri = process.env.NEO4J_URI;
  const username = process.env.NEO4J_USERNAME ?? process.env.NEO4J_USER;
  const password = process.env.NEO4J_PASSWORD;
  const database = process.env.NEO4J_DATABASE || "neo4j";

  if (!uri || !username || !password) {
    return {
      status: "not_configured",
      details: "Set NEO4J_URI, NEO4J_USERNAME/NEO4J_USER, NEO4J_PASSWORD, and NEO4J_DATABASE.",
    };
  }

  const started = Date.now();
  const driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
  try {
    await driver.executeQuery("RETURN 1 AS ok", {}, { database });
    return { status: "connected", latency_ms: Date.now() - started };
  } catch (error) {
    return {
      status: "error",
      latency_ms: Date.now() - started,
      details: error instanceof Error ? error.message : "Neo4j connection failed.",
    };
  } finally {
    await driver.close();
  }
}

async function checkDatabricks() {
  const host = process.env.DATABRICKS_HOST;
  const token = process.env.DATABRICKS_TOKEN;
  if (!host || !token) {
    return { status: "not_configured" };
  }
  const started = Date.now();
  const response = await fetch(`${host.replace(/\/$/, "")}/api/2.1/jobs/list?limit=1`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return {
    status: response.ok ? "connected" : "error",
    latency_ms: Date.now() - started,
    details: response.ok ? undefined : `HTTP ${response.status}`,
  };
}

export async function GET() {
  const [neo4jStatus, databricksStatus] = await Promise.all([checkNeo4j(), checkDatabricks()]);
  const neo4jOk = neo4jStatus.status === "connected" || neo4jStatus.status === "not_configured";
  const databricksOk =
    databricksStatus.status === "connected" || databricksStatus.status === "not_configured";

  return NextResponse.json({
    status: neo4jOk && databricksOk ? "healthy" : "degraded",
    version: "graphops-0.1.0",
    graph_backend: "neo4j",
    neo4j: neo4jStatus,
    databricks: databricksStatus,
    redis: { status: "not_required" },
    timestamp: new Date().toISOString(),
  });
}
