import { NextResponse } from "next/server";
import { buildGraphOpsAiCommandPlan } from "@/lib/graphopsAiPlanner";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const command = String(body.command ?? "").trim();
  if (!command) {
    return NextResponse.json({ error: "command is required." }, { status: 400 });
  }

  return NextResponse.json(await buildGraphOpsAiCommandPlan(command));
}
