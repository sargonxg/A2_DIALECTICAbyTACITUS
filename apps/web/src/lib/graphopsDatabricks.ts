export const DATABRICKS_RUN_ALLOWLIST = new Map([
  ["book-demo", "136658630245751"],
  ["complex-demo", "261036137711214"],
  ["benchmark", "278369455996320"],
]);

export function databricksConfig() {
  const host =
    process.env.DATABRICKS_HOST ||
    "https://dbc-69e04818-40fb.cloud.databricks.com";
  const token = process.env.DATABRICKS_TOKEN;
  return { host: host.replace(/\/$/, ""), token };
}

function safePathSegment(value: string) {
  return value.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 96) || "default";
}

export async function triggerDatabricksRun(key: string) {
  const jobId = DATABRICKS_RUN_ALLOWLIST.get(key);
  if (!jobId) {
    return {
      requested: true,
      enabled: false,
      error: "Job is not allowlisted for web triggering.",
    };
  }

  const { host, token } = databricksConfig();
  if (!token) {
    return {
      requested: true,
      enabled: false,
      jobId,
      error: "DATABRICKS_TOKEN is not configured in the deployment environment.",
    };
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
    return {
      requested: true,
      enabled: true,
      jobId,
      error: `Databricks API returned HTTP ${response.status}`,
      details: payload,
    };
  }

  return {
    requested: true,
    enabled: true,
    jobId,
    runId: payload.run_id,
    runPageUrl: payload.run_page_url,
    details: payload,
  };
}

export async function stageGraphOpsUploadToDatabricks(input: {
  workspaceId: string;
  caseId: string;
  extractionRunId: string;
  sourceTitle: string;
  sourceType: string;
  objective: string;
  ontologyProfile: string;
  text: string;
  counts: Record<string, number>;
}) {
  const { host, token } = databricksConfig();
  if (!token) {
    return {
      requested: true,
      enabled: false,
      uploaded: false,
      message: "DATABRICKS_TOKEN is not configured in the deployment environment.",
    };
  }

  const path = [
    "dbfs:/FileStore/tacitus/dialectica/uploads",
    safePathSegment(input.workspaceId),
    safePathSegment(input.caseId),
    `${safePathSegment(input.extractionRunId)}.json`,
  ].join("/");
  const workspacePath = [
    "/Shared/tacitus/dialectica/uploads",
    safePathSegment(input.workspaceId),
    safePathSegment(input.caseId),
    `${safePathSegment(input.extractionRunId)}.json`,
  ].join("/");
  const document = {
    kind: "tacitus.dialectica.graphops_upload.v1",
    workspace_id: input.workspaceId,
    case_id: input.caseId,
    extraction_run_id: input.extractionRunId,
    source_title: input.sourceTitle,
    source_type: input.sourceType,
    objective: input.objective,
    ontology_profile: input.ontologyProfile,
    counts: input.counts,
    text: input.text,
    staged_at: new Date().toISOString(),
  };
  const contents = Buffer.from(JSON.stringify(document, null, 2), "utf8").toString("base64");

  const response = await fetch(`${host}/api/2.0/dbfs/put`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ path, contents, overwrite: true }),
  });
  const payload = await response.json().catch(() => ({}));
  if (response.ok) {
    return {
      requested: true,
      enabled: true,
      uploaded: true,
      storage: "dbfs",
      path,
      message: "Staged source and extraction metadata to Databricks DBFS.",
    };
  }

  const parentPath = workspacePath.split("/").slice(0, -1).join("/");
  await fetch(`${host}/api/2.0/workspace/mkdirs`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ path: parentPath }),
  });
  const workspaceResponse = await fetch(`${host}/api/2.0/workspace/import`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      path: workspacePath,
      format: "AUTO",
      contents,
      overwrite: true,
    }),
  });
  const workspacePayload = await workspaceResponse.json().catch(() => ({}));
  if (!workspaceResponse.ok) {
    return {
      requested: true,
      enabled: true,
      uploaded: false,
      path,
      workspacePath,
      message: `Databricks staging failed. DBFS returned HTTP ${response.status}; Workspace import returned HTTP ${workspaceResponse.status}.`,
      details: { dbfs: payload, workspace: workspacePayload },
    };
  }

  return {
    requested: true,
    enabled: true,
    uploaded: true,
    storage: "workspace",
    path: workspacePath,
    dbfsFallback: path,
    message: "Staged source and extraction metadata to Databricks Workspace files.",
  };
}

export async function stageGraphOpsArtifactToDatabricks(input: {
  workspaceId: string;
  caseId: string;
  artifactType: string;
  artifactId: string;
  payload: Record<string, unknown>;
}) {
  const { host, token } = databricksConfig();
  if (!token) {
    return {
      requested: true,
      enabled: false,
      uploaded: false,
      message: "DATABRICKS_TOKEN is not configured in the deployment environment.",
    };
  }

  const workspacePath = [
    "/Shared/tacitus/dialectica/artifacts",
    safePathSegment(input.workspaceId),
    safePathSegment(input.caseId),
    safePathSegment(input.artifactType),
    `${safePathSegment(input.artifactId)}.json`,
  ].join("/");
  const contents = Buffer.from(JSON.stringify(input.payload, null, 2), "utf8").toString("base64");
  const parentPath = workspacePath.split("/").slice(0, -1).join("/");

  await fetch(`${host}/api/2.0/workspace/mkdirs`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ path: parentPath }),
  });
  const response = await fetch(`${host}/api/2.0/workspace/import`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      path: workspacePath,
      format: "AUTO",
      contents,
      overwrite: true,
    }),
  });
  const details = await response.json().catch(() => ({}));
  if (!response.ok) {
    return {
      requested: true,
      enabled: true,
      uploaded: false,
      path: workspacePath,
      message: `Databricks artifact staging returned HTTP ${response.status}.`,
      details,
    };
  }
  return {
    requested: true,
    enabled: true,
    uploaded: true,
    storage: "workspace",
    path: workspacePath,
    message: "Staged GraphOps artifact to Databricks Workspace files.",
  };
}
