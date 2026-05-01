import { NextResponse } from "next/server";
import { readGraphOpsRun } from "@/lib/graphopsRuns";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  try {
    const result = await readGraphOpsRun(id);
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Run not found." },
      { status: 404 },
    );
  }
}
