/**
 * Workspace-scoped API helpers for the ConflictCorpus dashboard.
 * Augments the existing api.ts with integration, reasoning, and theory endpoints.
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

function getApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("dialectica_api_key");
}

async function workspaceRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const apiKey = getApiKey();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(apiKey ? { "X-API-Key": apiKey } : {}),
    ...(options.headers as Record<string, string>),
  };
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Integration graph (situation layer) ──────────────────────────────────────

export interface IntegrationGraphResponse {
  workspace_id: string;
  nodes: IntegrationNode[];
  edges: IntegrationEdge[];
  metadata?: Record<string, unknown>;
}

export interface IntegrationNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  vx?: number;
  vy?: number;
}

export interface IntegrationEdge {
  id?: string;
  source: string;
  target: string;
  type: string;
  weight?: number;
}

export function fetchWorkspaceGraph(workspaceId: string): Promise<IntegrationGraphResponse> {
  return workspaceRequest<IntegrationGraphResponse>(
    `/v1/integration/graph/${workspaceId}`,
  );
}

// ── Reasoning traces ──────────────────────────────────────────────────────────

export interface ReasoningTrace {
  id: string;
  rules_fired: string[];
  conclusion: string;
  confidence_type: "deterministic" | "probabilistic";
  confidence_score: number;
  human_validated: boolean;
  human_verdict?: string;
  source_node_ids: string[];
  created_at?: string;
}

export interface ReasoningTracesResponse {
  traces: ReasoningTrace[];
  total: number;
}

export function fetchReasoningTraces(workspaceId: string): Promise<ReasoningTracesResponse> {
  return workspaceRequest<ReasoningTracesResponse>(
    `/v1/workspaces/${workspaceId}/reasoning/traces`,
  );
}

export interface ValidateTraceRequest {
  verdict: "confirmed" | "rejected";
  notes?: string;
}

export function validateTrace(
  workspaceId: string,
  traceId: string,
  verdict: "confirmed" | "rejected",
  notes?: string,
): Promise<ReasoningTrace> {
  return workspaceRequest<ReasoningTrace>(
    `/v1/workspaces/${workspaceId}/reasoning/${traceId}/validate`,
    {
      method: "POST",
      body: JSON.stringify({ verdict, notes } satisfies ValidateTraceRequest),
    },
  );
}

// ── Theory assessments ────────────────────────────────────────────────────────

export interface TheoryAssessment {
  framework_id: string;
  display_name: string;
  score: number;
  primary_questions: string[];
  key_propositions: string[];
  domain: string;
}

export interface TheoryAssessmentsResponse {
  assessments: TheoryAssessment[];
}

export function fetchTheoryAssessments(workspaceId: string): Promise<TheoryAssessmentsResponse> {
  return workspaceRequest<TheoryAssessmentsResponse>(
    `/v1/workspaces/${workspaceId}/theory/assessments`,
  );
}

// ── Graph mutations ────────────────────────────────────────────────────────────

export interface AddNodeRequest {
  type: string;
  label: string;
  properties?: Record<string, unknown>;
}

export interface AddEdgeRequest {
  source: string;
  target: string;
  type: string;
}

export function addNode(
  workspaceId: string,
  node: AddNodeRequest,
): Promise<IntegrationNode> {
  return workspaceRequest<IntegrationNode>(
    `/v1/workspaces/${workspaceId}/entities`,
    { method: "POST", body: JSON.stringify(node) },
  );
}

export function deleteNode(workspaceId: string, nodeId: string): Promise<void> {
  return workspaceRequest<void>(
    `/v1/workspaces/${workspaceId}/entities/${nodeId}`,
    { method: "DELETE" },
  );
}

export function addEdge(
  workspaceId: string,
  edge: AddEdgeRequest,
): Promise<IntegrationEdge> {
  return workspaceRequest<IntegrationEdge>(
    `/v1/workspaces/${workspaceId}/relationships`,
    { method: "POST", body: JSON.stringify(edge) },
  );
}
