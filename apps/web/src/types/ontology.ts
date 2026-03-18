export type NodeType =
  | "actor"
  | "conflict"
  | "event"
  | "issue"
  | "interest"
  | "norm"
  | "process"
  | "outcome"
  | "narrative"
  | "emotional_state"
  | "trust_state"
  | "power_dynamic"
  | "location"
  | "evidence"
  | "role";

export type OntologyTier = "essential" | "standard" | "full";

export type ConflictDomain =
  | "interpersonal"
  | "workplace"
  | "commercial"
  | "legal"
  | "political"
  | "armed";

export type ConflictScale = "micro" | "meso" | "macro" | "meta";

export type ConflictStatus =
  | "latent"
  | "emerging"
  | "escalating"
  | "stalemate"
  | "de_escalating"
  | "settled"
  | "resolved"
  | "transformed";

export type GlaslStage = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;

export type KriesbergPhase =
  | "emergence"
  | "escalation"
  | "de_escalation"
  | "settlement"
  | "post_settlement";

export interface ConflictNode {
  id: string;
  label: string;
  workspace_id: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
  source_text?: string;
  confidence: number;
  extraction_method?: string;
  metadata: Record<string, unknown>;
}

export interface Actor extends ConflictNode {
  name: string;
  actor_type: string;
  description?: string;
  aliases?: string[];
  conflict_mode?: string;
  batna_strength?: string;
}

export interface Conflict extends ConflictNode {
  name: string;
  description?: string;
  domain: ConflictDomain;
  scale: ConflictScale;
  status: ConflictStatus;
  glasl_stage?: GlaslStage;
  kriesberg_phase?: KriesbergPhase;
  started_at?: string;
  ended_at?: string;
}

export interface Event extends ConflictNode {
  name: string;
  event_type: string;
  description?: string;
  occurred_at?: string;
  severity?: number;
}

export interface Issue extends ConflictNode {
  name: string;
  description?: string;
  salience?: number;
}

export interface EdgeType {
  source_type: NodeType;
  target_type: NodeType;
  edge_type: string;
  properties: Record<string, string>;
}

export interface GraphEdge {
  id: string;
  source_id: string;
  target_id: string;
  edge_type: string;
  weight: number;
  confidence: number;
  properties: Record<string, unknown>;
  created_at: string;
}
