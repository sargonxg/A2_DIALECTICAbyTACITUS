import type { OntologyTier, ConflictDomain, ConflictScale, GlaslStage, KriesbergPhase } from "./ontology";

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  tenant_id: string;
  domain: ConflictDomain;
  scale: ConflictScale;
  tier: OntologyTier;
  glasl_stage?: GlaslStage;
  kriesberg_phase?: KriesbergPhase;
  status?: string;
  node_count: number;
  edge_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
  domain: ConflictDomain;
  scale: ConflictScale;
  tier: OntologyTier;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ExtractionRequest {
  workspace_id: string;
  text?: string;
  document_url?: string;
  tier: OntologyTier;
}

export interface ExtractionResult {
  id: string;
  workspace_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  nodes_extracted: number;
  edges_extracted: number;
  created_at: string;
  completed_at?: string;
  error?: string;
}

export interface AnalysisRequest {
  workspace_id: string;
  query: string;
  mode: AnalysisMode;
  include_theory?: boolean;
}

export type AnalysisMode =
  | "escalation"
  | "ripeness"
  | "trust"
  | "power"
  | "causal"
  | "narrative"
  | "general";

export interface AnalysisResult {
  id: string;
  query: string;
  mode: AnalysisMode;
  assessment: string;
  evidence: string[];
  theory_lens?: string;
  confidence: number;
  gaps: string[];
  suggested_questions: string[];
  subgraph_ids: string[];
}

export interface TheoryFramework {
  id: string;
  name: string;
  author: string;
  description: string;
  key_concepts: string[];
  diagnostic_questions: string[];
}

export interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
  last_used_at?: string;
  is_active: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  graph_backend: string;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  tenant_id: string;
  role: "admin" | "analyst" | "viewer";
  avatar_url?: string;
}

// Graph node — matches workspace graph endpoint response
export interface GraphNode {
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

export interface GraphEdge {
  id?: string;
  source: string;
  target: string;
  type: string;
  weight?: number;
  properties?: Record<string, unknown>;
}

export interface WorkspaceGraphResponse {
  workspace_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: Record<string, unknown>;
}

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

export interface ValidateTraceRequest {
  verdict: "confirmed" | "rejected" | "modified";
  notes?: string;
}

export interface ValidationResponse {
  trace_id: string;
  workspace_id: string;
  verdict: "confirmed" | "rejected" | "modified";
  validated_at: string;
  notes?: string;
}

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

export interface AddEntityRequest {
  type: string;
  label: string;
  properties?: Record<string, unknown>;
}

export interface AddRelationshipRequest {
  source: string;
  target: string;
  type: string;
}
