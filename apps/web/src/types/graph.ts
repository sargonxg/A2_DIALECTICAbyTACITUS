import type { NodeType } from "./ontology";

export interface GraphNode {
  id: string;
  label: string;
  node_type: NodeType;
  name: string;
  confidence: number;
  properties: Record<string, unknown>;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  vx?: number;
  vy?: number;
}

export interface GraphLink {
  id: string;
  source: string | GraphNode;
  target: string | GraphNode;
  edge_type: string;
  weight: number;
  confidence: number;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export type LayoutType = "force" | "hierarchy" | "radial" | "temporal";

export interface GraphFilters {
  nodeTypes: Set<NodeType>;
  edgeTypes: Set<string>;
  dateRange: [Date | null, Date | null];
  confidenceThreshold: number;
  searchQuery: string;
}

export interface GraphViewState {
  layout: LayoutType;
  filters: GraphFilters;
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  zoom: number;
  center: [number, number];
}
