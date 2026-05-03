import { NextResponse } from "next/server";
import { buildGraphOpsManifest } from "@/lib/graphopsManifest";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(buildGraphOpsManifest());
}
