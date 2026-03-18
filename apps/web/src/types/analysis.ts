export interface EscalationAssessment {
  glasl_stage: number;
  glasl_name: string;
  level: "win-win" | "win-lose" | "lose-lose";
  trend: "escalating" | "stable" | "de_escalating";
  evidence: string[];
  intervention: string;
}

export interface RipenessAssessment {
  mhs_score: number;
  meo_score: number;
  overall_ripeness: number;
  is_ripe: boolean;
  indicators: string[];
  recommendations: string[];
}

export interface TrustAssessment {
  pairs: TrustPair[];
  overall_trust: number;
  critical_breakdowns: string[];
}

export interface TrustPair {
  actor_a: string;
  actor_b: string;
  ability: number;
  benevolence: number;
  integrity: number;
  overall: number;
}

export interface PowerAnalysis {
  actors: PowerActor[];
  asymmetries: string[];
  recommendations: string[];
}

export interface PowerActor {
  id: string;
  name: string;
  power_score: number;
  power_bases: Record<string, number>;
  centrality: number;
}

export interface CausalChain {
  events: CausalEvent[];
  links: CausalLink[];
}

export interface CausalEvent {
  id: string;
  name: string;
  occurred_at?: string;
  significance: number;
}

export interface CausalLink {
  source_id: string;
  target_id: string;
  mechanism: string;
  confidence: number;
  pearl_level: "association" | "intervention" | "counterfactual";
}

export interface ReasoningStep {
  type: "retrieval" | "symbolic" | "generation";
  description: string;
  duration_ms: number;
  detail?: string;
}

export interface TheoryMatch {
  framework_id: string;
  framework_name: string;
  relevance_score: number;
  matching_patterns: string[];
  guidance: string;
}
