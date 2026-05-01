import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

function repoRoot() {
  const cwd = process.cwd();
  if (path.basename(cwd) === "web" && path.basename(path.dirname(cwd)) === "apps") {
    return path.resolve(cwd, "..", "..");
  }
  return cwd;
}

function artifactsDir() {
  return process.env.GRAPHOPS_LOCAL_ARTIFACT_DIR || path.join(repoRoot(), ".dialectica", "graphops", "artifacts");
}

function safeFileName(value: string) {
  return value.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 128) || "artifact";
}

export async function persistGraphOpsArtifact(input: {
  artifactType: string;
  artifactId: string;
  payload: Record<string, unknown>;
}) {
  const dir = path.join(artifactsDir(), safeFileName(input.artifactType));
  await mkdir(dir, { recursive: true });
  const filePath = path.join(dir, `${safeFileName(input.artifactId)}.json`);
  const document = {
    kind: "tacitus.dialectica.local_artifact.v1",
    artifactType: input.artifactType,
    artifactId: input.artifactId,
    savedAt: new Date().toISOString(),
    payload: input.payload,
  };
  await writeFile(filePath, JSON.stringify(document, null, 2), "utf8");
  return {
    enabled: true,
    saved: true,
    path: filePath,
    message: `Saved ${input.artifactType} artifact locally.`,
  };
}

