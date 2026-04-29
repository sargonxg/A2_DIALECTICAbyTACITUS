import neo4j, { type Driver, type Record as Neo4jRecord } from "neo4j-driver";
import { NextResponse } from "next/server";
import { sampleCypherQueries } from "@/data/graphops";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

let cachedDriver: Driver | null = null;

function getDriver() {
  if (cachedDriver) return cachedDriver;

  const uri = process.env.NEO4J_URI;
  const username = process.env.NEO4J_USERNAME ?? process.env.NEO4J_USER;
  const password = process.env.NEO4J_PASSWORD;

  if (!uri || !username || !password) {
    throw new Error("Neo4j environment variables are not configured.");
  }

  cachedDriver = neo4j.driver(uri, neo4j.auth.basic(username, password));
  return cachedDriver;
}

function serializeValue(value: unknown): unknown {
  if (neo4j.isInt(value)) return value.toNumber();
  if (Array.isArray(value)) return value.map(serializeValue);
  if (value && typeof value === "object") {
    if ("properties" in value && "labels" in value) {
      const node = value as { labels: string[]; properties: Record<string, unknown>; identity?: unknown };
      return {
        identity: serializeValue(node.identity),
        labels: node.labels,
        properties: serializeValue(node.properties),
      };
    }
    if ("properties" in value && "type" in value) {
      const rel = value as { type: string; properties: Record<string, unknown>; identity?: unknown };
      return {
        identity: serializeValue(rel.identity),
        type: rel.type,
        properties: serializeValue(rel.properties),
      };
    }
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => [key, serializeValue(item)]),
    );
  }
  return value;
}

function serializeRecord(record: Neo4jRecord) {
  return Object.fromEntries(record.keys.map((key) => [String(key), serializeValue(record.get(key))]));
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const queryId = String(body?.queryId ?? "");
  const workspaceId = String(body?.workspaceId ?? "");
  const query = sampleCypherQueries.find((item) => item.title === queryId);

  if (!query) {
    return NextResponse.json({ error: "Unknown allowlisted query." }, { status: 400 });
  }
  if (!workspaceId || workspaceId.length > 120) {
    return NextResponse.json({ error: "workspaceId is required." }, { status: 400 });
  }

  try {
    const driver = getDriver();
    const database = process.env.NEO4J_DATABASE || "neo4j";
    const session = driver.session({ database, defaultAccessMode: neo4j.session.READ });
    try {
      const result = await session.executeRead((tx) =>
        tx.run(query.cypher, { workspace_id: workspaceId }),
      );
      return NextResponse.json({
        cypher: query.cypher,
        records: result.records.map(serializeRecord),
      });
    } finally {
      await session.close();
    }
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Neo4j query failed.",
        cypher: query.cypher,
      },
      { status: 503 },
    );
  }
}
