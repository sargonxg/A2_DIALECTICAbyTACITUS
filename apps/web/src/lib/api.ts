import type {
  Workspace,
  CreateWorkspaceRequest,
  PaginatedResponse,
  ExtractionRequest,
  ExtractionResult,
  AnalysisRequest,
  AnalysisResult,
  TheoryFramework,
  ApiKey,
  HealthResponse,
  UserProfile,
} from "@/types/api";
import type { GraphData } from "@/types/graph";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const apiKey =
    typeof window !== "undefined" ? localStorage.getItem("dialectica_api_key") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(apiKey ? { "X-API-Key": apiKey } : {}),
    ...(options.headers as Record<string, string>),
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, body);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  health: () => request<HealthResponse>("/health"),

  // Workspaces
  listWorkspaces: (page = 1, pageSize = 20) =>
    request<PaginatedResponse<Workspace>>(
      `/v1/workspaces?page=${page}&page_size=${pageSize}`,
    ),
  getWorkspace: (id: string) => request<Workspace>(`/v1/workspaces/${id}`),
  createWorkspace: (data: CreateWorkspaceRequest) =>
    request<Workspace>("/v1/workspaces", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteWorkspace: (id: string) =>
    request<void>(`/v1/workspaces/${id}`, { method: "DELETE" }),

  // Graph
  getGraph: (workspaceId: string) =>
    request<GraphData>(`/v1/workspaces/${workspaceId}/graph`),
  getSubgraph: (workspaceId: string, nodeId: string, depth = 2) =>
    request<GraphData>(
      `/v1/workspaces/${workspaceId}/graph/subgraph?node_id=${nodeId}&depth=${depth}`,
    ),

  // Entities
  getEntities: (workspaceId: string, nodeType?: string) =>
    request<PaginatedResponse<Record<string, unknown>>>(
      `/v1/workspaces/${workspaceId}/entities${nodeType ? `?type=${nodeType}` : ""}`,
    ),
  getEntity: (workspaceId: string, entityId: string) =>
    request<Record<string, unknown>>(
      `/v1/workspaces/${workspaceId}/entities/${entityId}`,
    ),

  // Extraction
  extract: (data: ExtractionRequest) =>
    request<ExtractionResult>("/v1/extract", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getExtraction: (id: string) =>
    request<ExtractionResult>(`/v1/extract/${id}`),

  // Analysis (SSE streaming)
  analyzeStream: (data: AnalysisRequest): EventSource => {
    const apiKey =
      typeof window !== "undefined"
        ? localStorage.getItem("dialectica_api_key")
        : null;
    const params = new URLSearchParams({
      workspace_id: data.workspace_id,
      query: data.query,
      mode: data.mode,
      ...(data.include_theory ? { include_theory: "true" } : {}),
      ...(apiKey ? { api_key: apiKey } : {}),
    });
    return new EventSource(`${API_URL}/v1/analyze/stream?${params}`);
  },
  analyze: (data: AnalysisRequest) =>
    request<AnalysisResult>("/v1/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Theory
  listFrameworks: () => request<TheoryFramework[]>("/v1/theory/frameworks"),
  getFramework: (id: string) =>
    request<TheoryFramework>(`/v1/theory/frameworks/${id}`),
  theoryGraph: () => request<GraphData>("/v1/theory/graph"),
  matchTheory: (workspaceId: string) =>
    request<{ matches: Array<{ framework_id: string; relevance: number; guidance: string }> }>(
      `/v1/theory/match`,
      { method: "POST", body: JSON.stringify({ workspace_id: workspaceId }) },
    ),

  // API Keys
  listApiKeys: () => request<ApiKey[]>("/v1/developers/keys"),
  createApiKey: (name: string) =>
    request<ApiKey & { key: string }>("/v1/developers/keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  revokeApiKey: (id: string) =>
    request<void>(`/v1/developers/keys/${id}`, { method: "DELETE" }),

  // Admin
  listUsers: () => request<UserProfile[]>("/v1/admin/users"),
  adminListWorkspaces: () =>
    request<PaginatedResponse<Workspace>>("/v1/admin/workspaces"),
};

export { ApiError };
