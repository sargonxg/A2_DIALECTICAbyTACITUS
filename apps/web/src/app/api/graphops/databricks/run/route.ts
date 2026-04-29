import { NextResponse } from "next/server";
import { databricksJobs } from "@/data/graphops";
import { DATABRICKS_RUN_ALLOWLIST, triggerDatabricksRun } from "@/lib/graphopsDatabricks";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const key = String(body?.key ?? "");
  const jobId = DATABRICKS_RUN_ALLOWLIST.get(key);

  if (!jobId) {
    return NextResponse.json({ error: "Job is not allowlisted for web triggering." }, { status: 400 });
  }

  const result = await triggerDatabricksRun(key);
  if (!result.enabled) {
    return NextResponse.json(
      {
        error: result.error,
        job: databricksJobs.find((item) => item.jobId === jobId),
      },
      { status: 503 },
    );
  }
  if (result.error) {
    return NextResponse.json(
      { error: result.error, details: result.details },
      { status: 502 },
    );
  }

  return NextResponse.json(result.details ?? result);
}
