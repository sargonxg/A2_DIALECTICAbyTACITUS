import type { DemoScenarioId } from "./doors";

export const ACT_TITLES = [
  "Mission Framing",
  "The Three Doors",
  "Source Reveal",
  "Chunking",
  "GLiNER Pre-filter",
  "Gemini Flash Extraction",
  "Pydantic Validation",
  "Coreference Resolution",
  "Relationship Extraction",
  "Embedding Projection",
  "Write To Graph",
  "Handoff",
] as const;

const shared = [
  "Every conflict has a structure. The demo makes that structure inspectable before any reasoning claim is made.",
  "Pick a corpus. Each door asks a question that needs citations, theory, and graph state rather than a fluent paragraph.",
  "The source text is the contract. Everything downstream must cite back to text, source_ids, and timestamps.",
  "The pipeline splits text into overlapping 2,000-character chunks so entities are not lost at boundaries.",
  "GLiNER scores entity density locally before expensive extraction. This is a cost-control hop, not theatre.",
  "Gemini receives the active ontology tier and emits structured candidates, not free-form notes.",
  "Pydantic rejects invalid objects before they reach the graph. Repairs are explicit and failures are culled.",
  "Coreference collapses aliases into canonical actors, events, and concepts so analytics do not split the same entity.",
  "Relationships materialize as typed edges. The causal chains later used by Prompt 2 are born here.",
  "Embeddings place graph objects in semantic space, enabling similarity and retrieval across corpora.",
  "The graph write is the decisive moment: structured objects and edges are now queryable in the backend.",
  "Now the reasoning theatre can ask questions that depend on deterministic graph structure.",
];

export function narratorFor(_scenario: DemoScenarioId | null, act: number): string {
  return shared[act] ?? shared[0];
}
