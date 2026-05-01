import { NextResponse } from "next/server";
import { buildGraphOpsWorkbenchStatus } from "@/lib/graphopsWorkbench";
import { listGraphOpsBenchmarks, readGraphOpsBenchmark } from "@/lib/graphopsBenchmarkRuns";
import { listGraphOpsRuns, readGraphOpsRun } from "@/lib/graphopsRuns";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function neo4jConfigured() {
  return Boolean(
    process.env.NEO4J_URI &&
      (process.env.NEO4J_USERNAME || process.env.NEO4J_USER) &&
      process.env.NEO4J_PASSWORD,
  );
}

function databricksConfigured() {
  return Boolean(process.env.DATABRICKS_HOST && (process.env.DATABRICKS_TOKEN || process.env.DATABRICKS_CLIENT_ID));
}

export async function GET() {
  const [runs, benchmarks] = await Promise.all([listGraphOpsRuns(5), listGraphOpsBenchmarks(5)]);
  return NextResponse.json(
    buildGraphOpsWorkbenchStatus({
      recentRunCount: runs.length,
      recentBenchmarkCount: benchmarks.length,
      neo4jConfigured: neo4jConfigured(),
      databricksConfigured: databricksConfigured(),
    }),
  );
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  let extraction = body.extraction ?? null;
  let benchmark = body.benchmark ?? null;

  if (!extraction && body.extractionRunId) {
    extraction = await readGraphOpsRun(String(body.extractionRunId));
  }
  if (!benchmark && body.benchmarkId) {
    benchmark = await readGraphOpsBenchmark(String(body.benchmarkId));
  }

  const [runs, benchmarks] = await Promise.all([listGraphOpsRuns(5), listGraphOpsBenchmarks(5)]);
  return NextResponse.json(
    buildGraphOpsWorkbenchStatus({
      extraction,
      benchmark,
      recentRunCount: runs.length,
      recentBenchmarkCount: benchmarks.length,
      neo4jConfigured: neo4jConfigured(),
      databricksConfigured: databricksConfigured(),
    }),
  );
}
