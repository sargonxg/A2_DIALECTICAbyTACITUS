import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";

export type GraphOpsRunSummary = {
  extractionRunId: string;
  workspaceId: string;
  caseId: string;
  objective: string;
  ontologyProfile: string;
  savedAt: string;
  sourceTitle?: string;
  sourceType?: string;
  counts: Record<string, number>;
  quality?: Record<string, unknown>;
  ruleSignals?: number;
  localPath: string;
};

function repoRoot() {
  const cwd = process.cwd();
  if (path.basename(cwd) === "web" && path.basename(path.dirname(cwd)) === "apps") {
    return path.resolve(cwd, "..", "..");
  }
  return cwd;
}

function runsDir() {
  return process.env.GRAPHOPS_LOCAL_RUN_DIR || path.join(repoRoot(), ".dialectica", "graphops", "runs");
}

function safeFileName(value: string) {
  return value.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 128) || "run";
}

export async function persistGraphOpsRun(input: {
  result: Record<string, unknown>;
  sourceTitle: string;
  sourceType: string;
}) {
  const dir = runsDir();
  await mkdir(dir, { recursive: true });
  const extractionRunId = String(input.result.extractionRunId || `run_${Date.now()}`);
  const filePath = path.join(dir, `${safeFileName(extractionRunId)}.json`);
  const document = {
    kind: "tacitus.dialectica.local_run.v1",
    savedAt: new Date().toISOString(),
    sourceTitle: input.sourceTitle,
    sourceType: input.sourceType,
    result: input.result,
  };
  await writeFile(filePath, JSON.stringify(document, null, 2), "utf8");
  return {
    enabled: true,
    saved: true,
    path: filePath,
    message: "Saved run locally for reload and offline review.",
  };
}

export async function readGraphOpsRun(extractionRunId: string) {
  const filePath = path.join(runsDir(), `${safeFileName(extractionRunId)}.json`);
  const payload = JSON.parse(await readFile(filePath, "utf8")) as {
    result?: Record<string, unknown>;
  };
  return payload.result ?? payload;
}

export async function listGraphOpsRuns(limit = 20): Promise<GraphOpsRunSummary[]> {
  const dir = runsDir();
  let files: string[] = [];
  try {
    files = await readdir(dir);
  } catch {
    return [];
  }

  const summaries: Array<GraphOpsRunSummary | null> = await Promise.all(
    files
      .filter((file) => file.endsWith(".json"))
      .map(async (file) => {
        const filePath = path.join(dir, file);
        try {
          const payload = JSON.parse(await readFile(filePath, "utf8")) as {
            savedAt?: string;
            sourceTitle?: string;
            sourceType?: string;
            result?: Record<string, unknown>;
          };
          const result = payload.result ?? {};
          const ruleEvaluation = result.ruleEvaluation as
            | { summary?: { fired?: number } }
            | undefined;
          const summary: GraphOpsRunSummary = {
            extractionRunId: String(result.extractionRunId ?? path.basename(file, ".json")),
            workspaceId: String(result.workspaceId ?? ""),
            caseId: String(result.caseId ?? ""),
            objective: String(result.objective ?? ""),
            ontologyProfile: String(result.ontologyProfile ?? ""),
            savedAt: String(payload.savedAt ?? ""),
            counts: (result.counts as Record<string, number>) ?? {},
            ruleSignals: ruleEvaluation?.summary?.fired ?? 0,
            localPath: filePath,
          };
          if (payload.sourceTitle) summary.sourceTitle = payload.sourceTitle;
          if (payload.sourceType) summary.sourceType = payload.sourceType;
          if (result.quality) summary.quality = result.quality as Record<string, unknown>;
          return summary;
        } catch {
          return null;
        }
      }),
  );

  return summaries
    .filter((item): item is GraphOpsRunSummary => Boolean(item))
    .sort((a, b) => b.savedAt.localeCompare(a.savedAt))
    .slice(0, limit);
}
