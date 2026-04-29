import { NextResponse } from "next/server";
import { databricksJobs } from "@/data/graphops";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function databricksConfig() {
  const host =
    process.env.DATABRICKS_HOST ||
    "https://dbc-69e04818-40fb.cloud.databricks.com";
  const token = process.env.DATABRICKS_TOKEN;
  return { host: host.replace(/\/$/, ""), token };
}

export async function GET() {
  const { host, token } = databricksConfig();

  if (!token) {
    return NextResponse.json({
      mode: "configured-metadata",
      message: "Set DATABRICKS_TOKEN in the deployment environment for live run status.",
      jobs: databricksJobs,
    });
  }

  const response = await fetch(`${host}/api/2.1/jobs/runs/list?limit=25`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!response.ok) {
    return NextResponse.json(
      {
        mode: "error",
        message: `Databricks API returned HTTP ${response.status}`,
        jobs: databricksJobs,
      },
      { status: 502 },
    );
  }

  const payload = await response.json();
  const runs = Array.isArray(payload.runs) ? payload.runs : [];
  const byJobId = new Map<string, unknown[]>();

  for (const run of runs) {
    const jobId = String(run.job_id ?? "");
    if (!byJobId.has(jobId)) byJobId.set(jobId, []);
    byJobId.get(jobId)!.push(run);
  }

  return NextResponse.json({
    mode: "live",
    jobs: databricksJobs.map((job) => ({
      ...job,
      recentRuns: byJobId.get(job.jobId) ?? [],
    })),
  });
}
