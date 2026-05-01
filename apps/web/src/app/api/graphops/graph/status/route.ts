import { NextResponse } from "next/server";
import { getGraphOpsGraphStatus } from "@/lib/graphopsGraph";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const workspaceId = url.searchParams.get("workspaceId") || undefined;
  const caseId = url.searchParams.get("caseId") || undefined;
  return NextResponse.json(await getGraphOpsGraphStatus({ workspaceId, caseId }));
}
