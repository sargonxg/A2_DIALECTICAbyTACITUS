import { NextResponse } from "next/server";
import { databricksJobs } from "@/data/graphops";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const RUN_ALLOWLIST = new Map([
  ["book-demo", "136658630245751"],
  ["complex-demo", "261036137711214"],
  ["benchmark", "278369455996320"],
]);

function databricksConfig() {
  const host =
    process.env.DATABRICKS_HOST ||
    "https://dbc-69e04818-40fb.cloud.databricks.com";
  const token = process.env.DATABRICKS_TOKEN;
  return { host: host.replace(/\/$/, ""), token };
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const key = String(body?.key ?? "");
  const jobId = RUN_ALLOWLIST.get(key);

  if (!jobId) {
    return NextResponse.json({ error: "Job is not allowlisted for web triggering." }, { status: 400 });
  }

  const { host, token } = databricksConfig();
  if (!token) {
    return NextResponse.json(
      {
        error: "DATABRICKS_TOKEN is not configured in the deployment environment.",
        job: databricksJobs.find((item) => item.jobId === jobId),
      },
      { status: 503 },
    );
  }

  const response = await fetch(`${host}/api/2.1/jobs/run-now`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ job_id: Number(jobId) }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    return NextResponse.json(
      { error: `Databricks API returned HTTP ${response.status}`, details: payload },
      { status: 502 },
    );
  }

  return NextResponse.json(payload);
}
