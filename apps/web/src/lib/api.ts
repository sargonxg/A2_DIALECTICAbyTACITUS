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
  WorkspaceGraphResponse,
  GraphNode,
  GraphEdge,
  ReasoningTracesResponse,
  ValidateTraceRequest,
  ValidationResponse,
  TheoryAssessment,
  TheoryAssessmentsResponse,
  AddEntityRequest,
  AddRelationshipRequest,
} from "@/types/api";
import type { GraphData } from "@/types/graph";
import { getApiUrl } from "./config";

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
  const API_URL = getApiUrl();
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
    request<WorkspaceGraphResponse>(`/v1/workspaces/${workspaceId}/graph`),
  getSubgraph: (workspaceId: string, nodeId: string, depth = 2) =>
    request<WorkspaceGraphResponse>(
      `/v1/workspaces/${workspaceId}/graph/subgraph?node_id=${nodeId}&depth=${depth}`,
    ),

  // Entity mutations
  addEntity: (workspaceId: string, entity: AddEntityRequest) =>
    request<GraphNode>(`/v1/workspaces/${workspaceId}/entities`, {
      method: "POST",
      body: JSON.stringify(entity),
    }),
  deleteEntity: (workspaceId: string, entityId: string) =>
    request<void>(`/v1/workspaces/${workspaceId}/entities/${entityId}`, {
      method: "DELETE",
    }),

  // Relationship mutations
  addRelationship: (workspaceId: string, edge: AddRelationshipRequest) =>
    request<GraphEdge>(`/v1/workspaces/${workspaceId}/relationships`, {
      method: "POST",
      body: JSON.stringify(edge),
    }),

  // Reasoning traces
  getReasoningTraces: (workspaceId: string) =>
    request<ReasoningTracesResponse>(
      `/v1/workspaces/${workspaceId}/reasoning/traces`,
    ),
  validateTrace: (
    workspaceId: string,
    traceId: string,
    verdict: "confirmed" | "rejected" | "modified",
    notes?: string,
  ) =>
    request<ValidationResponse>(
      `/v1/workspaces/${workspaceId}/reasoning/${traceId}/validate`,
      {
        method: "POST",
        body: JSON.stringify({ verdict, notes } satisfies ValidateTraceRequest),
      },
    ),

  // Theory assessments
  getTheoryAssessments: (workspaceId: string) =>
    request<{ workspace_id: string; assessments: Array<Record<string, unknown>> }>(
      `/v1/workspaces/${workspaceId}/theory`,
    ).then((data): TheoryAssessmentsResponse => {
      const assessments: TheoryAssessment[] = (data.assessments ?? []).map((a) => ({
        framework_id: (a.framework_id ?? "") as string,
        display_name: (a.name ?? a.display_name ?? "") as string,
        score: (a.applicability ?? a.score ?? 0) as number,
        primary_questions: (a.insights ?? a.primary_questions ?? []) as string[],
        key_propositions: (a.indicators ?? a.key_propositions ?? []) as string[],
        domain: (a.domain ?? "universal") as string,
      }));
      return { assessments };
    }),

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
    request<ExtractionResult>(`/v1/workspaces/${data.workspace_id}/extract`, {
      method: "POST",
      body: JSON.stringify({
        text: data.text ?? "",
        source_url: data.document_url ?? "",
        tier: data.tier,
      }),
    }),
  getExtraction: (workspaceId: string, jobId: string) =>
    request<ExtractionResult>(
      `/v1/workspaces/${workspaceId}/extractions/${jobId}`,
    ),
  uploadDocument: (workspaceId: string, file: File, tier: string = "standard") => {
    const API_URL = getApiUrl();
    const apiKey =
      typeof window !== "undefined" ? localStorage.getItem("dialectica_api_key") : null;
    const form = new FormData();
    form.append("file", file);
    return fetch(
      `${API_URL}/v1/workspaces/${workspaceId}/extract/document?tier=${tier}`,
      {
        method: "POST",
        headers: apiKey ? { "X-API-Key": apiKey } : {},
        body: form,
      },
    ).then(async (res) => {
      if (!res.ok) throw new ApiError(res.status, await res.text());
      return res.json() as Promise<ExtractionResult>;
    });
  },

  // Gutenberg
  listGutenbergCatalog: () =>
    request<{
      books: Array<{
        book_id: string;
        title: string;
        author: string;
        domain: string;
        subdomain: string;
        summary: string;
        estimated_words: number;
        recommended_tier: string;
      }>;
    }>("/v1/gutenberg/catalog"),
  ingestGutenberg: (
    workspaceId: string,
    body: { book_id: string; title?: string; tier?: string; max_chars?: number },
  ) =>
    request<{
      job_id: string;
      workspace_id: string;
      book_id: string;
      title: string;
      status: string;
      fetched_chars: number;
      estimated_words: number;
      created_at: string;
    }>(`/v1/workspaces/${workspaceId}/ingest/gutenberg`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Live extraction progress (SSE)
  streamExtraction: (workspaceId: string, jobId: string): EventSource => {
    const API_URL = getApiUrl();
    const apiKey =
      typeof window !== "undefined"
        ? localStorage.getItem("dialectica_api_key")
        : null;
    const params = new URLSearchParams();
    if (apiKey) params.set("api_key", apiKey);
    return new EventSource(
      `${API_URL}/v1/workspaces/${workspaceId}/extractions/${jobId}/stream?${params}`,
    );
  },

  // Corpus library
  listCorpusDocuments: (workspaceId: string) =>
    request<{
      workspace_id: string;
      total_documents: number;
      total_words: number;
      total_nodes: number;
      total_edges: number;
      documents: Array<{
        id: string;
        title: string;
        content_hash: string;
        word_count: number;
        language: string;
        ingested_at: string;
        extraction_tier: string;
        extraction_model: string;
        nodes_extracted: number;
        edges_extracted: number;
        errors: number;
        job_id: string;
        source_kind: string;
        gutenberg_book_id: string | null;
      }>;
    }>(`/v1/workspaces/${workspaceId}/corpus/documents`),

  // Analysis (SSE streaming)
  analyzeStream: (data: AnalysisRequest): EventSource => {
    const API_URL = getApiUrl();
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

  // Benchmarks
  runBenchmark: (params: {
    corpus_id: string;
    tier: string;
    model: string;
    include_graph_augmented: boolean;
  }) =>
    request<Record<string, unknown>>("/v1/admin/benchmark/run", {
      method: "POST",
      body: JSON.stringify(params),
    }),
  getBenchmarkHistory: (limit = 50) =>
    request<Record<string, unknown>[]>(
      `/v1/admin/benchmark/history?limit=${limit}`,
    ),
  getBenchmarkResult: (id: string) =>
    request<Record<string, unknown>>(`/v1/admin/benchmark/${id}`),
};

export { ApiError };
