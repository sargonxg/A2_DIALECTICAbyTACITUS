import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import type { GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";

export type GraphOpsBenchmarkSummary = {
  benchmarkId: string;
  workspaceId: string;
  caseId: string;
  extractionRunId?: string;
  objective: string;
  question: string;
  overall: number;
  createdAt: string;
  localPath: string;
};

function repoRoot() {
  const cwd = process.cwd();
  if (path.basename(cwd) === "web" && path.basename(path.dirname(cwd)) === "apps") {
    return path.resolve(cwd, "..", "..");
  }
  return cwd;
}

function benchmarkDir() {
  return process.env.GRAPHOPS_LOCAL_BENCHMARK_DIR || path.join(repoRoot(), ".dialectica", "graphops", "benchmarks");
}

function safeFileName(value: string) {
  return value.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 128) || "benchmark";
}

export async function persistGraphOpsBenchmark(result: GraphOpsBenchmarkResult) {
  const dir = benchmarkDir();
  await mkdir(dir, { recursive: true });
  const filePath = path.join(dir, `${safeFileName(result.benchmarkId)}.json`);
  await writeFile(
    filePath,
    JSON.stringify(
      {
        kind: "tacitus.dialectica.local_benchmark.v1",
        savedAt: new Date().toISOString(),
        result,
      },
      null,
      2,
    ),
    "utf8",
  );
  return {
    enabled: true,
    saved: true,
    path: filePath,
    message: "Saved benchmark locally for repeatable comparison.",
  };
}

export async function readGraphOpsBenchmark(benchmarkId: string) {
  const filePath = path.join(benchmarkDir(), `${safeFileName(benchmarkId)}.json`);
  const payload = JSON.parse(await readFile(filePath, "utf8")) as { result?: GraphOpsBenchmarkResult };
  return payload.result ?? (payload as GraphOpsBenchmarkResult);
}

export async function listGraphOpsBenchmarks(limit = 20): Promise<GraphOpsBenchmarkSummary[]> {
  let files: string[] = [];
  try {
    files = await readdir(benchmarkDir());
  } catch {
    return [];
  }

  const summaries = await Promise.all(
    files
      .filter((file) => file.endsWith(".json"))
      .map(async (file) => {
        const filePath = path.join(benchmarkDir(), file);
        try {
          const payload = JSON.parse(await readFile(filePath, "utf8")) as { result?: GraphOpsBenchmarkResult };
          const result = payload.result;
          if (!result) return null;
          const summary: GraphOpsBenchmarkSummary = {
            benchmarkId: result.benchmarkId,
            workspaceId: result.workspaceId,
            caseId: result.caseId,
            objective: result.objective,
            question: result.question,
            overall: result.scores.overall,
            createdAt: result.createdAt,
            localPath: filePath,
          };
          if (result.extractionRunId) summary.extractionRunId = result.extractionRunId;
          return summary;
        } catch {
          return null;
        }
      }),
  );

  return summaries
    .filter((item): item is GraphOpsBenchmarkSummary => Boolean(item))
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    .slice(0, limit);
}
