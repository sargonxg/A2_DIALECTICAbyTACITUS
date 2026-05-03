import type { GraphData } from "@/types/graph";
import type { DemoScenarioId } from "../data/doors";

export interface ReasoningResultFixture {
  question_id: string;
  answer_summary: string;
  answer_full: string;
  confidence: number;
  determinism_score: number;
  primary_framework: string;
  cited_node_ids: string[];
  cited_edge_ids: string[];
  cypher_queries: string[];
  symbolic_rules_fired: string[];
  hallucination_risk: number;
  elapsed_ms: number;
  cost_usd: number;
}

export interface LLMComparisonFixture {
  model: string;
  captured_at: string;
  system_prompt: string;
  answer: string;
  tokens: number;
  wall_clock_ms: number;
}

export interface SimilarityNeighbor {
  workspace_id: string;
  conflict_name: string;
  semantic_dist: number;
  topological_dist: number;
  combined_dist: number;
  explanation: string;
}

export interface CounterfactualFixture {
  remove_label: string;
  removed_node_ids: string[];
  removed_edge_ids: string[];
  result_summary: string;
  diff: string;
}

export interface CuratedReasoningQuestion {
  id: string;
  scenario_id: DemoScenarioId;
  text: string;
  stake: string;
  academic_anchor: string;
  primary_framework: string;
  symbolic_rules: string[];
  counterfactual_supported: boolean;
  similarity_supported: boolean;
  dialectica: ReasoningResultFixture;
  llm: LLMComparisonFixture;
  counterfactual?: CounterfactualFixture;
  similarity?: SimilarityNeighbor[];
}

export interface ReasoningScenario {
  id: DemoScenarioId;
  title: string;
  subtitle: string;
  workspace_id: string;
  graph: GraphData;
  questions: CuratedReasoningQuestion[];
}
