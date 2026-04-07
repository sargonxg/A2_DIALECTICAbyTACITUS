/**
 * @tacitus/dialectica-sdk
 *
 * TypeScript SDK for the DIALECTICA API — The Universal Data Layer for Human Friction.
 *
 * Usage:
 *   import { createDialecticaClient } from "@tacitus/dialectica-sdk";
 *   const client = createDialecticaClient({ apiKey: "dk_..." });
 *   const workspaces = await client.workspaces.list();
 */

// Re-export generated OpenAPI types when available.
// After running `npm run generate`, the generated types will be at:
//   ./generated/api-types.ts
// Uncomment the following line once types have been generated:
// export type * from "./generated/api-types";

// ─── Core Types ──────────────────────────────────────────────────────────────

export interface ClientOptions {
  /** Base URL of the DIALECTICA API. Defaults to "http://localhost:8080". */
  baseUrl?: string;
  /** API key for authentication. */
  apiKey: string;
  /** Optional custom fetch implementation (for testing or Node 16). */
  fetch?: typeof globalThis.fetch;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

// ─── Workspace Types ─────────────────────────────────────────────────────────

export interface Workspace {
  id: string;
  name: string;
  domain: string;
  scale: string;
  tier: string;
  description: string;
  tenant_id: string;
  created_at: string;
  node_count: number;
  edge_count: number;
}

export interface WorkspaceCreate {
  name: string;
  domain?: string;
  scale?: string;
  tier?: string;
  description?: string;
}

export interface WorkspaceUpdate {
  name?: string;
  domain?: string;
  scale?: string;
  description?: string;
}

// ─── Entity Types ────────────────────────────────────────────────────────────

export interface Entity {
  id: string;
  label: string;
  name: string;
  properties: Record<string, unknown>;
  confidence: number;
}

export interface EntityCreate {
  label: string;
  name: string;
  properties?: Record<string, unknown>;
  confidence?: number;
}

// ─── Relationship Types ──────────────────────────────────────────────────────

export interface Relationship {
  id: string;
  type: string;
  source_id: string;
  target_id: string;
  properties: Record<string, unknown>;
  weight: number;
}

// ─── Extraction Types ────────────────────────────────────────────────────────

export interface ExtractRequest {
  text: string;
  source_url?: string;
  source_title?: string;
  tier?: string;
}

export interface ExtractionJob {
  job_id: string;
  workspace_id: string;
  status: "pending" | "running" | "complete" | "failed";
  created_at: string;
  completed_at: string | null;
  nodes_extracted: number;
  edges_extracted: number;
  error: string | null;
}

// ─── Graph Types ─────────────────────────────────────────────────────────────

export interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    name: string;
    confidence: number;
  }>;
  edges: Array<{
    id: string;
    type: string;
    source: string;
    target: string;
    weight: number;
  }>;
}

export interface GraphStats {
  workspace_id: string;
  total_nodes: number;
  total_edges: number;
  node_type_counts: Record<string, number>;
  edge_type_counts: Record<string, number>;
}

export interface SubgraphData {
  center_id: string;
  nodes: Array<Record<string, unknown>>;
  edges: Array<Record<string, unknown>>;
  hops: number;
}

export interface SearchResult {
  node_id: string;
  label: string;
  name: string;
  score: number;
}

// ─── Reasoning Types ─────────────────────────────────────────────────────────

export interface AnalyzeRequest {
  query: string;
  mode?: string;
  top_k?: number;
  hops?: number;
}

export interface EscalationAssessment {
  stage: string;
  stage_number: number | null;
  level: string;
  confidence: number;
  intervention_type: string;
  evidence: unknown[];
  signals: Array<{
    type: string;
    description: string;
    severity: string;
  }>;
  forecast: {
    direction: string;
    confidence: number;
    trajectory: Array<{
      timestamp: string;
      predicted_stage: string;
      confidence: number;
    }>;
  };
}

export interface RipenessAssessment {
  mhs_score: number;
  meo_score: number;
  overall_score: number;
  is_ripe: boolean;
  factors: Record<string, unknown>;
}

export interface PowerAnalysis {
  dyads: Array<{
    actor_id: string;
    target_id: string;
    total_power: number;
    asymmetry: number;
  }>;
  most_powerful: string;
  average_asymmetry: number;
  asymmetries: Array<{
    actor_a: string;
    actor_b: string;
    advantage_holder: string;
    score: number;
    recommendation: string;
  }>;
}

export interface TrustAnalysis {
  average_trust: number;
  lowest_trust_pair: unknown;
  highest_trust_pair: unknown;
  dyads: Array<{
    trustor: string;
    trustee: string;
    ability: number;
    benevolence: number;
    integrity: number;
    overall: number;
  }>;
  recent_changes: Array<{
    trustor: string;
    trustee: string;
    delta: number;
    type: string;
    event: string;
  }>;
}

export interface CausationAnalysis {
  chains: Array<{
    root: string;
    depth: number;
    has_cycle: boolean;
    length: number;
  }>;
  root_causes: Array<{
    event_id: string;
    description: string;
    downstream: number;
  }>;
}

export interface NetworkAnalysis {
  centrality: Array<{
    actor_id: string;
    betweenness: number;
    closeness: number;
    degree: number;
  }>;
  communities: Array<{
    id: string;
    size: number;
    actors: string[];
  }>;
  polarisation: {
    modularity: number;
    level: string;
    num_communities: number;
  };
  brokers: Array<{
    actor_id: string;
    betweenness: number;
    mediation_potential: number;
  }>;
}

export interface QualityDashboard {
  workspace_id: string;
  overall_quality: number;
  completeness: {
    score: number;
    tier: string;
    missing_node_types: string[];
    orphan_nodes: number;
  };
  consistency: {
    score: number;
    edge_violations: number;
  };
  coverage: {
    score: number;
    avg_confidence: number;
    temporal_span_days: number;
  };
  recommendations: string[];
  assessed_at: string;
}

// ─── Theory Types ────────────────────────────────────────────────────────────

export interface TheoryFramework {
  id: string;
  name: string;
  [key: string]: unknown;
}

export interface TheoryAssessment {
  workspace_id: string;
  top_framework: string;
  synthesis: string;
  assessments: Array<{
    framework_id: string;
    name: string;
    applicability: number;
    insights: string[];
    indicators: string[];
  }>;
}

export interface FrameworkAssessment {
  framework_id: string;
  name: string;
  applicability: number;
  insights: string[];
  indicators: string[];
  limitations: string[];
}

// ─── Integration Types ──────────────────────────────────────────────────────

export interface GraphSnapshotNode {
  id: string;
  label: string;
  name: string;
  properties: Record<string, unknown>;
  confidence: number;
}

export interface GraphSnapshotEdge {
  id: string;
  type: string;
  source_id: string;
  target_id: string;
  weight: number;
}

export interface GraphSnapshot {
  workspace_id: string;
  nodes: GraphSnapshotNode[];
  edges: GraphSnapshotEdge[];
  node_count: number;
  edge_count: number;
  subdomain: string | null;
  escalation_stage: number | null;
  ripeness_score: number | null;
}

export interface ConflictContext {
  workspace_id: string;
  context_text: string;
  key_actors: string[];
  key_issues: string[];
  escalation_summary: string;
  theory_recommendation: string;
}

export interface QueryResult {
  answer: string;
  confidence: number;
  citations: Array<Record<string, unknown>>;
  reasoning_trace: string[];
  escalation_stage: number | null;
  patterns_detected: string[];
}

export interface QueryConflictParams {
  workspaceId: string;
  query: string;
  mode?: string;
}

// ─── SDK Error ───────────────────────────────────────────────────────────────

export class DialecticaError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly detail?: unknown,
  ) {
    super(message);
    this.name = "DialecticaError";
  }
}

// ─── Resource Classes ────────────────────────────────────────────────────────

class BaseResource {
  constructor(
    protected readonly baseUrl: string,
    protected readonly headers: Record<string, string>,
    protected readonly fetchFn: typeof globalThis.fetch,
  ) {}

  protected async request<T>(
    method: string,
    path: string,
    body?: unknown,
    query?: Record<string, string | number | boolean | undefined>,
  ): Promise<T> {
    const url = new URL(path, this.baseUrl);
    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value !== undefined) {
          url.searchParams.set(key, String(value));
        }
      }
    }

    const init: RequestInit = {
      method,
      headers: {
        ...this.headers,
        ...(body ? { "Content-Type": "application/json" } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    };

    const response = await this.fetchFn(url.toString(), init);

    if (!response.ok) {
      let detail: unknown;
      try {
        detail = await response.json();
      } catch {
        detail = await response.text();
      }
      throw new DialecticaError(
        `DIALECTICA API error: ${response.status} ${response.statusText}`,
        response.status,
        detail,
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json() as Promise<T>;
  }
}

// ─── Workspaces ──────────────────────────────────────────────────────────────

class WorkspacesResource extends BaseResource {
  /** List all workspaces for the current tenant. */
  async list(): Promise<Workspace[]> {
    return this.request<Workspace[]>("GET", "/v1/workspaces");
  }

  /** Get a single workspace by ID. */
  async get(workspaceId: string): Promise<Workspace> {
    return this.request<Workspace>("GET", `/v1/workspaces/${workspaceId}`);
  }

  /** Create a new workspace. */
  async create(data: WorkspaceCreate): Promise<Workspace> {
    return this.request<Workspace>("POST", "/v1/workspaces", data);
  }

  /** Update an existing workspace. */
  async update(workspaceId: string, data: WorkspaceUpdate): Promise<Workspace> {
    return this.request<Workspace>("PATCH", `/v1/workspaces/${workspaceId}`, data);
  }

  /** Delete a workspace. */
  async delete(workspaceId: string): Promise<void> {
    return this.request<void>("DELETE", `/v1/workspaces/${workspaceId}`);
  }
}

// ─── Entities ────────────────────────────────────────────────────────────────

class EntitiesResource extends BaseResource {
  /** List entities in a workspace. */
  async list(
    workspaceId: string,
    params?: PaginationParams & { label?: string },
  ): Promise<Entity[]> {
    return this.request<Entity[]>(
      "GET",
      `/v1/workspaces/${workspaceId}/entities`,
      undefined,
      params,
    );
  }

  /** Get a single entity by ID. */
  async get(workspaceId: string, entityId: string): Promise<Entity> {
    return this.request<Entity>(
      "GET",
      `/v1/workspaces/${workspaceId}/entities/${entityId}`,
    );
  }

  /** Delete an entity. */
  async delete(
    workspaceId: string,
    entityId: string,
    hard = false,
  ): Promise<void> {
    return this.request<void>(
      "DELETE",
      `/v1/workspaces/${workspaceId}/entities/${entityId}`,
      undefined,
      { hard },
    );
  }
}

// ─── Relationships ───────────────────────────────────────────────────────────

class RelationshipsResource extends BaseResource {
  /** List relationships in a workspace. */
  async list(
    workspaceId: string,
    params?: { edge_type?: string; limit?: number },
  ): Promise<Relationship[]> {
    return this.request<Relationship[]>(
      "GET",
      `/v1/workspaces/${workspaceId}/relationships`,
      undefined,
      params,
    );
  }

  /** Delete a relationship. */
  async delete(workspaceId: string, edgeId: string): Promise<void> {
    return this.request<void>(
      "DELETE",
      `/v1/workspaces/${workspaceId}/relationships/${edgeId}`,
    );
  }
}

// ─── Extraction ──────────────────────────────────────────────────────────────

class ExtractionResource extends BaseResource {
  /** Extract conflict entities from text. */
  async extractText(
    workspaceId: string,
    data: ExtractRequest,
  ): Promise<ExtractionJob> {
    return this.request<ExtractionJob>(
      "POST",
      `/v1/workspaces/${workspaceId}/extract`,
      data,
    );
  }

  /** List extraction jobs for a workspace. */
  async listJobs(workspaceId: string): Promise<ExtractionJob[]> {
    return this.request<ExtractionJob[]>(
      "GET",
      `/v1/workspaces/${workspaceId}/extractions`,
    );
  }

  /** Get status of an extraction job. */
  async getJob(workspaceId: string, jobId: string): Promise<ExtractionJob> {
    return this.request<ExtractionJob>(
      "GET",
      `/v1/workspaces/${workspaceId}/extractions/${jobId}`,
    );
  }
}

// ─── Graph ───────────────────────────────────────────────────────────────────

class GraphResource extends BaseResource {
  /** Get full workspace graph (nodes + edges). */
  async get(workspaceId: string, limit?: number): Promise<GraphData> {
    return this.request<GraphData>(
      "GET",
      `/v1/workspaces/${workspaceId}/graph`,
      undefined,
      { limit },
    );
  }

  /** Get workspace graph statistics. */
  async stats(workspaceId: string): Promise<GraphStats> {
    return this.request<GraphStats>(
      "GET",
      `/v1/workspaces/${workspaceId}/graph/stats`,
    );
  }

  /** Get N-hop subgraph centered on a node. */
  async subgraph(
    workspaceId: string,
    centerId: string,
    hops = 2,
  ): Promise<SubgraphData> {
    return this.request<SubgraphData>(
      "GET",
      `/v1/workspaces/${workspaceId}/graph/subgraph`,
      undefined,
      { center_id: centerId, hops },
    );
  }

  /** Search within the workspace graph. */
  async search(
    workspaceId: string,
    query: string,
    limit = 20,
  ): Promise<SearchResult[]> {
    return this.request<SearchResult[]>(
      "GET",
      `/v1/workspaces/${workspaceId}/graph/search`,
      undefined,
      { q: query, limit },
    );
  }
}

// ─── Reasoning ───────────────────────────────────────────────────────────────

class ReasoningResource extends BaseResource {
  /**
   * Analyze a conflict workspace (returns SSE stream).
   * Use the raw fetch response for streaming; this method returns the Response
   * directly so callers can process the event stream.
   */
  async analyzeStream(
    workspaceId: string,
    data: AnalyzeRequest,
  ): Promise<Response> {
    const url = new URL(
      `/v1/workspaces/${workspaceId}/analyze`,
      this.baseUrl,
    );
    const response = await this.fetchFn(url.toString(), {
      method: "POST",
      headers: {
        ...this.headers,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new DialecticaError(
        `DIALECTICA API error: ${response.status}`,
        response.status,
      );
    }

    return response;
  }

  /** Get Glasl escalation assessment for the workspace. */
  async escalation(workspaceId: string): Promise<EscalationAssessment> {
    return this.request<EscalationAssessment>(
      "GET",
      `/v1/workspaces/${workspaceId}/escalation`,
    );
  }

  /** Get Zartman ripeness assessment. */
  async ripeness(workspaceId: string): Promise<RipenessAssessment> {
    return this.request<RipenessAssessment>(
      "GET",
      `/v1/workspaces/${workspaceId}/ripeness`,
    );
  }

  /** Get French/Raven power map. */
  async power(workspaceId: string): Promise<PowerAnalysis> {
    return this.request<PowerAnalysis>(
      "GET",
      `/v1/workspaces/${workspaceId}/power`,
    );
  }

  /** Get Mayer/Davis/Schoorman trust matrix. */
  async trust(workspaceId: string): Promise<TrustAnalysis> {
    return this.request<TrustAnalysis>(
      "GET",
      `/v1/workspaces/${workspaceId}/trust`,
    );
  }

  /** Get causal chain analysis. */
  async causation(workspaceId: string): Promise<CausationAnalysis> {
    return this.request<CausationAnalysis>(
      "GET",
      `/v1/workspaces/${workspaceId}/causation`,
    );
  }

  /** Get graph quality metrics. */
  async quality(workspaceId: string): Promise<QualityDashboard> {
    return this.request<QualityDashboard>(
      "GET",
      `/v1/workspaces/${workspaceId}/quality`,
    );
  }

  /** Get network topology metrics. */
  async network(workspaceId: string): Promise<NetworkAnalysis> {
    return this.request<NetworkAnalysis>(
      "GET",
      `/v1/workspaces/${workspaceId}/network`,
    );
  }
}

// ─── Theory ──────────────────────────────────────────────────────────────────

class TheoryResource extends BaseResource {
  /** List all conflict theory frameworks. */
  async listFrameworks(): Promise<TheoryFramework[]> {
    return this.request<TheoryFramework[]>("GET", "/v1/theory/frameworks");
  }

  /** Get a specific theory framework. */
  async getFramework(frameworkId: string): Promise<TheoryFramework> {
    return this.request<TheoryFramework>(
      "GET",
      `/v1/theory/frameworks/${frameworkId}`,
    );
  }

  /** Apply all 15 frameworks to a workspace. */
  async applyAll(workspaceId: string): Promise<TheoryAssessment> {
    return this.request<TheoryAssessment>(
      "GET",
      `/v1/workspaces/${workspaceId}/theory`,
    );
  }

  /** Apply a specific framework to a workspace. */
  async applyFramework(
    workspaceId: string,
    frameworkId: string,
  ): Promise<FrameworkAssessment> {
    return this.request<FrameworkAssessment>(
      "GET",
      `/v1/workspaces/${workspaceId}/theory/${frameworkId}`,
    );
  }
}

// ─── Integration ────────────────────────────────────────────────────────────

class IntegrationResource extends BaseResource {
  /** Get full graph snapshot for a workspace (admin only). */
  async getGraphSnapshot(workspaceId: string): Promise<GraphSnapshot> {
    return this.request<GraphSnapshot>(
      "GET",
      `/v1/integration/graph/${workspaceId}`,
    );
  }

  /** Get structured conflict context for Praxis (admin only). */
  async getConflictContext(workspaceId: string): Promise<ConflictContext> {
    return this.request<ConflictContext>(
      "GET",
      `/v1/integration/context/${workspaceId}`,
    );
  }

  /** Execute a conflict analysis query (admin only). */
  async queryConflict(params: QueryConflictParams): Promise<QueryResult> {
    return this.request<QueryResult>("POST", "/v1/integration/query", {
      workspace_id: params.workspaceId,
      query: params.query,
      mode: params.mode ?? "general",
    });
  }
}

// ─── Main Client ─────────────────────────────────────────────────────────────

export class DialecticaClient {
  public readonly workspaces: WorkspacesResource;
  public readonly entities: EntitiesResource;
  public readonly relationships: RelationshipsResource;
  public readonly extraction: ExtractionResource;
  public readonly graph: GraphResource;
  public readonly reasoning: ReasoningResource;
  public readonly theory: TheoryResource;
  public readonly integration: IntegrationResource;

  constructor(options: ClientOptions) {
    const baseUrl = (options.baseUrl ?? "http://localhost:8080").replace(
      /\/$/,
      "",
    );
    const fetchFn = options.fetch ?? globalThis.fetch.bind(globalThis);
    const headers: Record<string, string> = {
      Authorization: `Bearer ${options.apiKey}`,
      Accept: "application/json",
    };

    this.workspaces = new WorkspacesResource(baseUrl, headers, fetchFn);
    this.entities = new EntitiesResource(baseUrl, headers, fetchFn);
    this.relationships = new RelationshipsResource(baseUrl, headers, fetchFn);
    this.extraction = new ExtractionResource(baseUrl, headers, fetchFn);
    this.graph = new GraphResource(baseUrl, headers, fetchFn);
    this.reasoning = new ReasoningResource(baseUrl, headers, fetchFn);
    this.theory = new TheoryResource(baseUrl, headers, fetchFn);
    this.integration = new IntegrationResource(baseUrl, headers, fetchFn);
  }
}

// ─── Factory ─────────────────────────────────────────────────────────────────

/**
 * Convenience factory for creating a DialecticaClient.
 *
 * @example
 * ```ts
 * import { createDialecticaClient } from "@tacitus/dialectica-sdk";
 *
 * const client = createDialecticaClient({
 *   apiKey: process.env.DIALECTICA_API_KEY!,
 *   baseUrl: "https://api.dialectica.ai",
 * });
 *
 * const workspaces = await client.workspaces.list();
 * const stats = await client.graph.stats("ws-123");
 * const escalation = await client.reasoning.escalation("ws-123");
 * ```
 */
export function createDialecticaClient(
  options: ClientOptions,
): DialecticaClient {
  return new DialecticaClient(options);
}
