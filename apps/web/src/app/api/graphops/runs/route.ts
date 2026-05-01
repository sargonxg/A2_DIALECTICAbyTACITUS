import { NextResponse } from "next/server";
import { listGraphOpsRuns } from "@/lib/graphopsRuns";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const limit = Math.min(Number(url.searchParams.get("limit") || 20), 100);
  const runs = await listGraphOpsRuns(Number.isFinite(limit) ? limit : 20);
  return NextResponse.json({
    mode: "local_filesystem",
    runs,
  });
}
