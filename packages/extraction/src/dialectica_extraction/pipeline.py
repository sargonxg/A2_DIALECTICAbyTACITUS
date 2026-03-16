"""
Extraction Pipeline — LangGraph DAG for conflict entity extraction.

10-step pipeline:
  1. chunk_document → 2. gliner_prefilter → 3. extract_entities →
  4. validate_schema → 5. repair_extraction → 6. extract_relationships →
  7. resolve_coreference → 8. validate_structural → 9. compute_embeddings →
  10. write_to_graph

Conditional edges: validate_schema → repair if errors, skip if valid, abort if max retries.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, TypedDict

from dialectica_ontology.primitives import ConflictNode, NODE_TYPES
from dialectica_ontology.relationships import ConflictRelationship
from dialectica_ontology.tiers import OntologyTier, TIER_NODES

from dialectica_extraction.gliner_ner import GLiNERPreFilter, PrefilterResult
from dialectica_extraction.gemini import GeminiExtractor, GeminiExtractionResult
from dialectica_extraction.embeddings import EmbeddingService
from dialectica_extraction.validators.schema import validate_raw_nodes, validate_raw_edges
from dialectica_extraction.validators.structural import validate_structural
from dialectica_extraction.validators.temporal import validate_temporal
from dialectica_extraction.validators.symbolic import validate_symbolic
from dialectica_extraction.extractors.entity import enrich_actors, deduplicate_nodes
from dialectica_extraction.extractors.coreference import find_coreferences, merge_coreferent_nodes
from dialectica_extraction.extractors.relationship import apply_relationship_scoring

logger = logging.getLogger(__name__)

MAX_REPAIR_RETRIES = 3
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200


# ── State Types ────────────────────────────────────────────────────────────


@dataclass
class TextChunk:
    """A chunk of source text with position metadata."""

    text: str
    index: int
    start: int
    end: int


@dataclass
class ExtractionError:
    """An error that occurred during extraction."""

    step: str
    message: str
    details: dict = field(default_factory=dict)


class ExtractionState(TypedDict, total=False):
    """State flowing through the LangGraph pipeline."""

    text: str
    tier: str  # OntologyTier value
    workspace_id: str
    tenant_id: str
    chunks: list[dict]  # serialized TextChunks
    prefilter_results: list[dict]
    raw_entities: list[dict]
    validated_nodes: list[dict]  # serialized ConflictNodes
    validated_edges: list[dict]  # serialized ConflictRelationships
    invalid_entities: list[dict]
    validation_errors: list[str]
    embeddings: dict[str, list[float]]
    errors: list[dict]
    retry_count: int
    processing_time: dict[str, float]
    ingestion_stats: dict[str, int]

    # Intermediate: deserialized objects (not part of TypedDict, used internally)
    _nodes: list[Any]
    _edges: list[Any]


# ── Pipeline Nodes ─────────────────────────────────────────────────────────


def chunk_document(state: ExtractionState) -> ExtractionState:
    """Step 1: Split text into overlapping chunks preserving sentence boundaries."""
    start = time.time()
    text = state.get("text", "")
    chunks: list[dict] = []

    if len(text) <= CHUNK_SIZE:
        chunks.append({"text": text, "index": 0, "start": 0, "end": len(text)})
    else:
        pos = 0
        idx = 0
        while pos < len(text):
            end = min(pos + CHUNK_SIZE, len(text))

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence-ending punctuation near the end
                search_start = max(pos + CHUNK_SIZE - 200, pos)
                for boundary_char in [".\n", ".\r", ". ", "!\n", "! ", "?\n", "? "]:
                    last_boundary = text.rfind(boundary_char, search_start, end)
                    if last_boundary > search_start:
                        end = last_boundary + len(boundary_char)
                        break

            chunk_text = text[pos:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "index": idx,
                    "start": pos,
                    "end": end,
                })
                idx += 1

            # Advance with overlap
            pos = end - CHUNK_OVERLAP if end < len(text) else len(text)

    state["chunks"] = chunks
    state.setdefault("processing_time", {})["chunk_document"] = time.time() - start
    state.setdefault("errors", [])
    state.setdefault("retry_count", 0)
    return state


def gliner_prefilter(state: ExtractionState) -> ExtractionState:
    """Step 2: GLiNER pre-filter for entity-dense passage selection."""
    start = time.time()
    chunks = state.get("chunks", [])
    chunk_texts = [c["text"] for c in chunks]

    try:
        prefilter = GLiNERPreFilter()
        results = prefilter.prefilter(chunk_texts)
        state["prefilter_results"] = [
            {
                "chunk_index": r.chunk_index,
                "entity_count": r.entity_count,
                "entity_density": r.entity_density,
                "priority_score": r.priority_score,
            }
            for r in results
        ]
    except Exception as e:
        logger.warning("GLiNER prefilter failed: %s (passing all chunks)", e)
        state["prefilter_results"] = [
            {"chunk_index": i, "entity_count": 0, "entity_density": 0, "priority_score": 1.0}
            for i in range(len(chunks))
        ]

    state["processing_time"]["gliner_prefilter"] = time.time() - start
    return state


def extract_entities(state: ExtractionState) -> ExtractionState:
    """Step 3: Call Gemini Flash with tier-appropriate schema."""
    start = time.time()
    chunks = state.get("chunks", [])
    tier = OntologyTier(state.get("tier", "essential"))
    prefilter_results = state.get("prefilter_results", [])

    # Sort by priority, process highest-priority chunks first
    sorted_indices = sorted(
        range(len(prefilter_results)),
        key=lambda i: prefilter_results[i].get("priority_score", 1.0),
        reverse=True,
    )

    all_raw_entities: list[dict] = []

    try:
        extractor = GeminiExtractor()
        for idx in sorted_indices:
            if idx >= len(chunks):
                continue
            chunk = chunks[idx]
            result = extractor.extract_entities(chunk["text"], tier)
            if result.error:
                state["errors"].append({
                    "step": "extract_entities",
                    "message": result.error,
                    "details": {"chunk_index": idx},
                })
                continue

            # Tag each entity with its source chunk
            for entity in result.raw_nodes:
                entity.setdefault("_chunk_index", idx)
                entity.setdefault("source_text", entity.get("source_text", chunk["text"][:200]))
            all_raw_entities.extend(result.raw_nodes)
    except Exception as e:
        logger.error("Entity extraction failed: %s", e)
        state["errors"].append({
            "step": "extract_entities",
            "message": str(e),
        })

    state["raw_entities"] = all_raw_entities
    state["processing_time"]["extract_entities"] = time.time() - start
    return state


def validate_schema(state: ExtractionState) -> ExtractionState:
    """Step 4: Pydantic validation of extracted entities."""
    start = time.time()
    raw = state.get("raw_entities", [])
    tier = OntologyTier(state.get("tier", "essential"))
    ws = state.get("workspace_id", "")
    tid = state.get("tenant_id", "")

    result = validate_raw_nodes(raw, tier, workspace_id=ws, tenant_id=tid)

    # Serialize validated nodes
    state["validated_nodes"] = [n.model_dump(mode="json") for n in result.valid_nodes]
    state["invalid_entities"] = result.invalid_entities
    state["validation_errors"] = result.errors
    state["_nodes"] = result.valid_nodes

    state["processing_time"]["validate_schema"] = time.time() - start
    return state


def repair_extraction(state: ExtractionState) -> ExtractionState:
    """Step 5: Send validation errors back to Gemini for repair."""
    start = time.time()
    invalid = state.get("invalid_entities", [])
    errors = state.get("validation_errors", [])
    retry_count = state.get("retry_count", 0)
    tier = OntologyTier(state.get("tier", "essential"))

    if not invalid or retry_count >= MAX_REPAIR_RETRIES:
        state["processing_time"]["repair_extraction"] = time.time() - start
        return state

    try:
        extractor = GeminiExtractor()
        repair_result = extractor.repair_entities(invalid, errors, tier)

        if repair_result.raw_nodes:
            # Re-validate repaired entities
            ws = state.get("workspace_id", "")
            tid = state.get("tenant_id", "")
            validation = validate_raw_nodes(repair_result.raw_nodes, tier, ws, tid)

            # Add newly valid nodes
            existing_nodes = state.get("_nodes", [])
            existing_nodes.extend(validation.valid_nodes)
            state["_nodes"] = existing_nodes
            state["validated_nodes"] = [n.model_dump(mode="json") for n in existing_nodes]

            # Update invalid/errors
            state["invalid_entities"] = validation.invalid_entities
            state["validation_errors"] = validation.errors
    except Exception as e:
        logger.warning("Repair failed: %s", e)

    state["retry_count"] = retry_count + 1
    state["processing_time"]["repair_extraction"] = time.time() - start
    return state


def extract_relationships(state: ExtractionState) -> ExtractionState:
    """Step 6: Gemini call for edge extraction."""
    start = time.time()
    validated_nodes = state.get("validated_nodes", [])
    text = state.get("text", "")
    tier = OntologyTier(state.get("tier", "essential"))

    if not validated_nodes:
        state["validated_edges"] = []
        state["_edges"] = []
        state["processing_time"]["extract_relationships"] = time.time() - start
        return state

    try:
        extractor = GeminiExtractor()
        # Simplify entities for prompt
        entity_summaries = []
        for n in validated_nodes:
            summary = {"id": n.get("id"), "label": n.get("label")}
            for field in ("name", "description", "content"):
                if field in n:
                    summary[field] = n[field]
            entity_summaries.append(summary)

        result = extractor.extract_relationships(entity_summaries, text, tier)

        if result.error:
            state["errors"].append({
                "step": "extract_relationships",
                "message": result.error,
            })
            state["validated_edges"] = []
            state["_edges"] = []
        else:
            ws = state.get("workspace_id", "")
            tid = state.get("tenant_id", "")
            node_ids = {n.get("id") for n in validated_nodes}
            edge_validation = validate_raw_edges(
                result.raw_edges, tier, node_ids=node_ids, workspace_id=ws, tenant_id=tid
            )
            state["validated_edges"] = [e.model_dump(mode="json") for e in edge_validation.valid_edges]
            state["_edges"] = edge_validation.valid_edges

            if edge_validation.errors:
                state["errors"].extend([
                    {"step": "extract_relationships", "message": err}
                    for err in edge_validation.errors
                ])
    except Exception as e:
        logger.error("Relationship extraction failed: %s", e)
        state["errors"].append({"step": "extract_relationships", "message": str(e)})
        state["validated_edges"] = []
        state["_edges"] = []

    state["processing_time"]["extract_relationships"] = time.time() - start
    return state


def resolve_coreference(state: ExtractionState) -> ExtractionState:
    """Step 7: Cross-chunk entity merging and coreference resolution."""
    start = time.time()
    nodes = state.get("_nodes", [])
    edges = state.get("_edges", [])

    if not nodes:
        state["processing_time"]["resolve_coreference"] = time.time() - start
        return state

    # Enrich actors with aliases
    nodes = enrich_actors(nodes)

    # Find coreferences
    matches = find_coreferences(nodes)

    if matches:
        merged_nodes, merge_map = merge_coreferent_nodes(nodes, matches)

        # Update edge references
        for edge in edges:
            if edge.source_id in merge_map:
                edge.source_id = merge_map[edge.source_id]
            if edge.target_id in merge_map:
                edge.target_id = merge_map[edge.target_id]

        state["_nodes"] = merged_nodes
        state["validated_nodes"] = [n.model_dump(mode="json") for n in merged_nodes]
        logger.info("Merged %d coreferent node pairs", len(matches))

    # Deduplicate within batch
    state["_nodes"] = deduplicate_nodes(state.get("_nodes", []))
    state["validated_nodes"] = [n.model_dump(mode="json") for n in state["_nodes"]]

    state["processing_time"]["resolve_coreference"] = time.time() - start
    return state


def validate_structural_step(state: ExtractionState) -> ExtractionState:
    """Step 8: Conflict Grammar structural rules validation."""
    start = time.time()
    nodes = state.get("_nodes", [])
    edges = state.get("_edges", [])

    # Structural validation
    structural = validate_structural(nodes, edges)
    if structural.errors:
        state["errors"].extend([
            {"step": "validate_structural", "message": err}
            for err in structural.errors
        ])
    if structural.warnings:
        for w in structural.warnings:
            logger.warning("Structural: %s", w)

    # Temporal validation
    temporal = validate_temporal(nodes, edges)
    if temporal.errors:
        state["errors"].extend([
            {"step": "validate_temporal", "message": err}
            for err in temporal.errors
        ])

    # Symbolic validation
    symbolic = validate_symbolic(nodes, edges)
    if symbolic.warnings:
        for w in symbolic.warnings:
            logger.info("Symbolic: %s", w)

    # Apply relationship scoring
    state["_edges"] = apply_relationship_scoring(edges)

    state["processing_time"]["validate_structural"] = time.time() - start
    return state


def compute_embeddings(state: ExtractionState) -> ExtractionState:
    """Step 9: Generate embeddings for all validated nodes."""
    start = time.time()
    nodes = state.get("_nodes", [])

    if not nodes:
        state["embeddings"] = {}
        state["processing_time"]["compute_embeddings"] = time.time() - start
        return state

    try:
        service = EmbeddingService(use_vertex=True)
        embeddings = service.embed_nodes(nodes)
        state["embeddings"] = embeddings

        # Update nodes with embeddings
        for node in nodes:
            if node.id in embeddings:
                node.embedding = embeddings[node.id]

        state["_nodes"] = nodes
        state["validated_nodes"] = [n.model_dump(mode="json") for n in nodes]
    except Exception as e:
        logger.warning("Embedding computation failed: %s", e)
        state["embeddings"] = {}

    state["processing_time"]["compute_embeddings"] = time.time() - start
    return state


def write_to_graph(state: ExtractionState) -> ExtractionState:
    """Step 10: Batch upsert all nodes and edges to graph database."""
    start = time.time()
    nodes = state.get("_nodes", [])
    edges = state.get("_edges", [])

    state["ingestion_stats"] = {
        "nodes_written": len(nodes),
        "edges_written": len(edges),
        "errors": len(state.get("errors", [])),
    }

    # Note: actual graph write requires an async GraphClient.
    # In production, this step calls:
    #   await graph_client.batch_upsert_nodes(nodes, workspace_id, tenant_id)
    #   await graph_client.batch_upsert_edges(edges, workspace_id, tenant_id)
    # For the synchronous LangGraph pipeline, we store the data for
    # the caller to persist.

    state["processing_time"]["write_to_graph"] = time.time() - start
    return state


# ── Routing Functions ──────────────────────────────────────────────────────


def should_repair(state: ExtractionState) -> str:
    """Routing: should we attempt repair or proceed?"""
    invalid = state.get("invalid_entities", [])
    retry_count = state.get("retry_count", 0)

    if not invalid:
        return "skip_repair"
    if retry_count >= MAX_REPAIR_RETRIES:
        return "max_retries"
    return "repair"


# ── Graph Builder ──────────────────────────────────────────────────────────


def build_pipeline():
    """Build and return the LangGraph extraction pipeline.

    Returns a compiled StateGraph or a simple sequential pipeline
    if LangGraph is not available.
    """
    try:
        from langgraph.graph import StateGraph, END

        graph = StateGraph(ExtractionState)

        # Add nodes
        graph.add_node("chunk_document", chunk_document)
        graph.add_node("gliner_prefilter", gliner_prefilter)
        graph.add_node("extract_entities", extract_entities)
        graph.add_node("validate_schema", validate_schema)
        graph.add_node("repair_extraction", repair_extraction)
        graph.add_node("extract_relationships", extract_relationships)
        graph.add_node("resolve_coreference", resolve_coreference)
        graph.add_node("validate_structural", validate_structural_step)
        graph.add_node("compute_embeddings", compute_embeddings)
        graph.add_node("write_to_graph", write_to_graph)

        # Set entry point
        graph.set_entry_point("chunk_document")

        # Linear edges
        graph.add_edge("chunk_document", "gliner_prefilter")
        graph.add_edge("gliner_prefilter", "extract_entities")
        graph.add_edge("extract_entities", "validate_schema")

        # Conditional: validate -> repair or skip
        graph.add_conditional_edges(
            "validate_schema",
            should_repair,
            {
                "repair": "repair_extraction",
                "skip_repair": "extract_relationships",
                "max_retries": "extract_relationships",
            },
        )
        graph.add_conditional_edges(
            "repair_extraction",
            should_repair,
            {
                "repair": "repair_extraction",
                "skip_repair": "extract_relationships",
                "max_retries": "extract_relationships",
            },
        )

        # Continue after relationships
        graph.add_edge("extract_relationships", "resolve_coreference")
        graph.add_edge("resolve_coreference", "validate_structural")
        graph.add_edge("validate_structural", "compute_embeddings")
        graph.add_edge("compute_embeddings", "write_to_graph")
        graph.add_edge("write_to_graph", END)

        return graph.compile()

    except ImportError:
        logger.warning("LangGraph not available; using sequential pipeline")
        return None


class ExtractionPipeline:
    """High-level extraction pipeline wrapper.

    Builds a LangGraph DAG if available, otherwise runs steps sequentially.
    """

    def __init__(self) -> None:
        self._compiled = build_pipeline()

    def run(
        self,
        text: str,
        tier: OntologyTier = OntologyTier.ESSENTIAL,
        workspace_id: str = "",
        tenant_id: str = "",
    ) -> ExtractionState:
        """Run the extraction pipeline on input text.

        Args:
            text: Source document text.
            tier: Ontology tier for extraction.
            workspace_id: Target workspace.
            tenant_id: Owning tenant.

        Returns:
            ExtractionState with all extraction results.
        """
        initial_state: ExtractionState = {
            "text": text,
            "tier": tier.value,
            "workspace_id": workspace_id,
            "tenant_id": tenant_id,
            "chunks": [],
            "prefilter_results": [],
            "raw_entities": [],
            "validated_nodes": [],
            "validated_edges": [],
            "invalid_entities": [],
            "validation_errors": [],
            "embeddings": {},
            "errors": [],
            "retry_count": 0,
            "processing_time": {},
            "ingestion_stats": {},
            "_nodes": [],
            "_edges": [],
        }

        if self._compiled is not None:
            return self._compiled.invoke(initial_state)

        # Sequential fallback
        return self._run_sequential(initial_state)

    def _run_sequential(self, state: ExtractionState) -> ExtractionState:
        """Run pipeline steps sequentially without LangGraph."""
        steps = [
            chunk_document,
            gliner_prefilter,
            extract_entities,
            validate_schema,
        ]

        for step in steps:
            state = step(state)

        # Repair loop
        while state.get("invalid_entities") and state.get("retry_count", 0) < MAX_REPAIR_RETRIES:
            state = repair_extraction(state)
            if not state.get("invalid_entities"):
                break

        remaining_steps = [
            extract_relationships,
            resolve_coreference,
            validate_structural_step,
            compute_embeddings,
            write_to_graph,
        ]

        for step in remaining_steps:
            state = step(state)

        return state
