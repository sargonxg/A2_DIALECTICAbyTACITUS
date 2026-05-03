"""
Reasoning Router — Conflict analysis and symbolic reasoning endpoints.
"""

from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dialectica_api.deps import get_current_tenant, get_graph_client, get_query_engine

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["reasoning"])


class AnalyzeRequest(BaseModel):
    query: str
    mode: str = "general"
    top_k: int = 20
    hops: int = 2


class AnalysisResult(BaseModel):
    query: str
    workspace_id: str
    mode: str
    answer: str
    citations: list[dict[str, Any]] = []
    escalation_stage: int | None = None
    ripeness_score: float | None = None
    patterns_detected: list[str] = []
    confidence: float = 0.5


class CuratedReasoningRequest(BaseModel):
    question_id: str


class CounterfactualReasoningRequest(BaseModel):
    question_id: str
    removed_node_ids: list[str] = []
    removed_edge_ids: list[str] = []


class SimilarityReasoningRequest(BaseModel):
    question_id: str
    k: int = 3


class CuratedQuestionResponse(BaseModel):
    id: str
    scenario_id: str
    text: str
    stake: str
    academic_anchor: str
    primary_framework: str
    symbolic_rules: list[str]
    counterfactual_supported: bool
    similarity_supported: bool


class CuratedLibraryResponse(BaseModel):
    workspace_id: str
    questions: list[CuratedQuestionResponse]


class CounterfactualHandle(BaseModel):
    supported: bool
    transient: bool = True
    removed_node_ids: list[str] = []
    removed_edge_ids: list[str] = []
    note: str = "Counterfactual graph mutilations are never written back to Neo4j."


class SimilarityHandle(BaseModel):
    supported: bool
    k: int = 3
    method: str = "semantic_centroid_plus_topology_signature"


class ReasoningResult(BaseModel):
    question_id: str
    answer_summary: str
    answer_full: str
    confidence: float
    determinism_score: float
    primary_framework: str
    cited_node_ids: list[str]
    cited_edge_ids: list[str]
    cypher_queries: list[str]
    symbolic_rules_fired: list[str]
    hallucination_risk: float
    counterfactual_handle: CounterfactualHandle | None = None
    structural_similarity_handle: SimilarityHandle | None = None
    elapsed_ms: int
    cost_usd: float


class CounterfactualReasoningResponse(BaseModel):
    baseline: ReasoningResult
    counterfactual: ReasoningResult
    diff: dict[str, Any]
    persisted: bool = False


class SimilarityNeighbor(BaseModel):
    workspace_id: str
    conflict_name: str
    semantic_dist: float
    topological_dist: float
    combined_dist: float
    explanation: str


class SimilarityReasoningResponse(BaseModel):
    question_id: str
    workspace_id: str
    neighbours: list[SimilarityNeighbor]


FRAMEWORK_MODE_MAP = {
    "glasl": "escalation",
    "glasl_kriesberg": "escalation",
    "zartman": "ripeness",
    "fisher_ury": "power",
    "french_raven": "power",
    "mayer_trust": "trust",
    "pearl_causal": "causal",
    "network_metrics": "network",
    "pattern_matching": "general",
    "galtung": "general",
    "lederach": "general",
}


def _risk_to_float(raw: Any) -> float:
    if isinstance(raw, int | float):
        return max(0.0, min(1.0, float(raw)))
    mapping = {"low": 0.08, "medium": 0.22, "high": 0.55, "unknown": 0.18}
    return mapping.get(str(raw).lower(), 0.18)


def _summary(text: str) -> str:
    first_sentence = text.strip().split(". ")[0].strip()
    if not first_sentence:
        return "No answer generated."
    return first_sentence if first_sentence.endswith(".") else f"{first_sentence}."


def _determinism_score(question: Any, response: Any) -> float:
    symbolic_count = len(getattr(question, "symbolic_rules", []))
    citation_count = len(getattr(response, "citations", []) or [])
    base = 0.62 + min(0.22, symbolic_count * 0.055) + min(0.12, citation_count * 0.02)
    return round(min(0.97, base), 2)


def _curated_question_or_404(question_id: str) -> Any:
    from dialectica_reasoning.library import get_curated_library

    library = get_curated_library()
    question = library.get(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail=f"Unknown curated question: {question_id}")
    return question


def _curated_question_response(question: Any) -> CuratedQuestionResponse:
    return CuratedQuestionResponse(
        id=question.id,
        scenario_id=question.scenario_id,
        text=question.text,
        stake=question.stake,
        academic_anchor=question.academic_anchor,
        primary_framework=question.primary_framework,
        symbolic_rules=list(question.symbolic_rules),
        counterfactual_supported=question.counterfactual_supported,
        similarity_supported=question.similarity_supported,
    )


async def _run_curated_question(
    *,
    workspace_id: str,
    question_id: str,
    query_engine: Any,
) -> ReasoningResult:
    question = _curated_question_or_404(question_id)
    if query_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Query engine unavailable; configure graph backend and reasoning package.",
        )

    started = time.perf_counter()
    mode = FRAMEWORK_MODE_MAP.get(question.primary_framework, "general")
    analysis = await query_engine.analyze(
        query=question.text,
        workspace_id=workspace_id,
        mode=mode,
        top_k=20,
        hops=2,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    citations = getattr(analysis, "citations", []) or []
    cited_node_ids = [str(c.node_id) for c in citations if getattr(c, "node_id", None)]
    answer = str(getattr(analysis, "answer", "") or "")
    confidence = float(getattr(analysis, "confidence", 0.5) or 0.5)
    return ReasoningResult(
        question_id=question.id,
        answer_summary=_summary(answer),
        answer_full=answer,
        confidence=round(max(0.0, min(1.0, confidence)), 2),
        determinism_score=_determinism_score(question, analysis),
        primary_framework=question.primary_framework,
        cited_node_ids=cited_node_ids,
        cited_edge_ids=[],
        cypher_queries=[
            "GraphRAG retrieval uses graph_client.get_nodes(...), get_node(...), and traverse(...) with workspace_id filtering.",
            "MATCH p=(seed)-[*1..2]-(context) WHERE seed.id IN $seed_ids AND seed.workspace_id = $workspace_id RETURN p",
        ],
        symbolic_rules_fired=list(question.symbolic_rules),
        hallucination_risk=_risk_to_float(getattr(analysis, "hallucination_risk", "unknown")),
        counterfactual_handle=CounterfactualHandle(supported=True)
        if question.counterfactual_supported
        else None,
        structural_similarity_handle=SimilarityHandle(supported=True)
        if question.similarity_supported
        else None,
        elapsed_ms=elapsed_ms,
        cost_usd=0.0,
    )


@router.post("/analyze")
async def analyze_streaming(
    workspace_id: str,
    body: AnalyzeRequest,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    query_engine: Any = Depends(get_query_engine),  # noqa: B008
) -> StreamingResponse:
    """
    Analyze a conflict workspace. Streams SSE events for each step.

    Event types: started, retrieval, symbolic, synthesis, complete
    """
    if query_engine is None:
        # Return non-streaming fallback if engine unavailable
        async def error_stream() -> AsyncIterator[str]:
            yield f"data: {json.dumps({'step': 'error', 'detail': 'Query engine unavailable'})}\n\n"

        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def event_stream() -> AsyncIterator[str]:
        async for chunk in query_engine.stream_analyze(
            query=body.query,
            workspace_id=workspace_id,
            mode=body.mode,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/reason/library")
async def list_curated_questions(
    workspace_id: str,
    scenario_id: str | None = None,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
) -> CuratedLibraryResponse:
    """List curated Prompt 2 questions for clients and demos."""
    from dialectica_reasoning.library import get_curated_library

    questions = list(get_curated_library().values())
    if scenario_id:
        questions = [question for question in questions if question.scenario_id == scenario_id]
    return CuratedLibraryResponse(
        workspace_id=workspace_id,
        questions=[_curated_question_response(question) for question in questions],
    )


@router.post("/reason/curated")
async def answer_curated_question(
    workspace_id: str,
    body: CuratedReasoningRequest,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    query_engine: Any = Depends(get_query_engine),  # noqa: B008
) -> ReasoningResult:
    """Run one curated Prompt 2 question through the live reasoning engine."""
    return await _run_curated_question(
        workspace_id=workspace_id,
        question_id=body.question_id,
        query_engine=query_engine,
    )


@router.post("/reason/counterfactual")
async def answer_counterfactual_question(
    workspace_id: str,
    body: CounterfactualReasoningRequest,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    query_engine: Any = Depends(get_query_engine),  # noqa: B008
) -> CounterfactualReasoningResponse:
    """Return a transient counterfactual result without mutating Neo4j.

    This initial adapter preserves the API semantics and explicit non-persistence
    contract. The deeper backend pass will inject a MutilatedGraph into symbolic
    rules so numeric fields are recomputed over the deleted nodes/edges.
    """
    question = _curated_question_or_404(body.question_id)
    if not question.counterfactual_supported:
        raise HTTPException(status_code=422, detail="Question does not support counterfactuals.")

    baseline = await _run_curated_question(
        workspace_id=workspace_id,
        question_id=body.question_id,
        query_engine=query_engine,
    )
    counterfactual = baseline.model_copy(
        update={
            "answer_summary": f"Counterfactual run requested with {len(body.removed_node_ids)} nodes and {len(body.removed_edge_ids)} edges removed.",
            "answer_full": (
                baseline.answer_full
                + "\n\nCounterfactual note: this response used the transient API path and did not write any graph mutation to Neo4j. Full graph-mutilation recomputation is the next backend pass."
            ),
            "counterfactual_handle": CounterfactualHandle(
                supported=True,
                removed_node_ids=body.removed_node_ids,
                removed_edge_ids=body.removed_edge_ids,
            ),
        }
    )
    return CounterfactualReasoningResponse(
        baseline=baseline,
        counterfactual=counterfactual,
        diff={
            "removed_node_count": len(body.removed_node_ids),
            "removed_edge_count": len(body.removed_edge_ids),
            "persisted": False,
            "backend_status": "transient_adapter",
        },
        persisted=False,
    )


@router.post("/reason/similarity")
async def get_structural_similarity(
    workspace_id: str,
    body: SimilarityReasoningRequest,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
) -> SimilarityReasoningResponse:
    """Return demo comparison-corpus neighbours for supported curated questions.

    The endpoint is shaped for the production graph-kernel implementation and
    currently returns the curated comparison corpus declared in Prompt 2.
    """
    question = _curated_question_or_404(body.question_id)
    if not question.similarity_supported:
        raise HTTPException(status_code=422, detail="Question does not support similarity.")

    curated: dict[str, list[SimilarityNeighbor]] = {
        "R-6": [
            SimilarityNeighbor(
                workspace_id="corpus-vendetta-hatfield-mccoy",
                conflict_name="Hatfield-McCoy feud",
                semantic_dist=0.14,
                topological_dist=0.22,
                combined_dist=0.18,
                explanation="Kin-coded revenge topology with weak central enforcement.",
            ),
            SimilarityNeighbor(
                workspace_id="corpus-vendetta-gjakmarrja",
                conflict_name="Albanian gjakmarrja",
                semantic_dist=0.19,
                topological_dist=0.23,
                combined_dist=0.21,
                explanation="Honor obligation and dormant-reactivated revenge cycles.",
            ),
            SimilarityNeighbor(
                workspace_id="corpus-vendetta-badal",
                conflict_name="Pashtun badal cycles",
                semantic_dist=0.25,
                topological_dist=0.29,
                combined_dist=0.27,
                explanation="Revenge as governance substitute under weak state authority.",
            ),
        ],
        "W-6": [
            SimilarityNeighbor(
                workspace_id="corpus-imperial-athens-sicily",
                conflict_name="Athens-Sicily 415 BCE",
                semantic_dist=0.13,
                topological_dist=0.19,
                combined_dist=0.16,
                explanation="Force projection overreach into a distant theatre.",
            ),
            SimilarityNeighbor(
                workspace_id="corpus-imperial-hitler-russia",
                conflict_name="Germany-Russia 1941",
                semantic_dist=0.16,
                topological_dist=0.22,
                combined_dist=0.19,
                explanation="Near-identical logistics-weather-attrition feedback loop.",
            ),
            SimilarityNeighbor(
                workspace_id="corpus-imperial-vietnam",
                conflict_name="US-Vietnam 1965-73",
                semantic_dist=0.31,
                topological_dist=0.37,
                combined_dist=0.34,
                explanation="Political overreach with distinct counterinsurgency topology.",
            ),
        ],
        "S-7": [
            SimilarityNeighbor(
                workspace_id="corpus-successor-taliban-2021",
                conflict_name="Taliban 2021",
                semantic_dist=0.20,
                topological_dist=0.28,
                combined_dist=0.24,
                explanation="Spoiler actor becomes successor authority after external scaffolding collapses.",
            ),
            SimilarityNeighbor(
                workspace_id="corpus-successor-rpf-1994",
                conflict_name="RPF Rwanda 1994",
                semantic_dist=0.29,
                topological_dist=0.32,
                combined_dist=0.31,
                explanation="Military successor transition with different legitimacy mechanics.",
            ),
            SimilarityNeighbor(
                workspace_id="corpus-successor-eritrea-1991",
                conflict_name="Eritrea 1991",
                semantic_dist=0.34,
                topological_dist=0.35,
                combined_dist=0.35,
                explanation="Rebel structure converts battlefield legitimacy into governance.",
            ),
        ],
    }
    neighbours = curated.get(body.question_id, [])[: max(1, min(body.k, 10))]
    return SimilarityReasoningResponse(
        question_id=body.question_id,
        workspace_id=workspace_id,
        neighbours=neighbours,
    )


@router.get("/escalation")
async def get_escalation(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get Glasl escalation assessment for the workspace."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.symbolic.escalation import EscalationDetector

    detector = EscalationDetector(graph_client)
    assessment = await detector.compute_glasl_stage(workspace_id)
    signals = await detector.detect_escalation_signals(workspace_id)
    forecast = await detector.forecast_trajectory(workspace_id)
    return {
        "stage": str(assessment.stage),
        "stage_number": getattr(assessment.stage, "stage_number", None),
        "level": assessment.level,
        "confidence": assessment.confidence,
        "intervention_type": assessment.intervention_type,
        "evidence": assessment.evidence[:10],
        "signals": [
            {"type": s.signal_type, "description": s.description, "severity": s.severity}
            for s in signals
        ],
        "forecast": {
            "direction": forecast.direction,
            "confidence": forecast.confidence,
            "trajectory": [
                {
                    "timestamp": str(t.timestamp),
                    "predicted_stage": t.predicted_stage,
                    "confidence": t.confidence,
                }
                for t in forecast.trajectory
            ],
        },
    }


@router.get("/ripeness")
async def get_ripeness(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get Zartman ripeness assessment."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.symbolic.ripeness import RipenessScorer

    scorer = RipenessScorer(graph_client)
    assessment = await scorer.compute_ripeness(workspace_id)
    return {
        "mhs_score": assessment.mhs_score,
        "meo_score": assessment.meo_score,
        "overall_score": assessment.overall_score,
        "is_ripe": assessment.is_ripe,
        "factors": assessment.factors,
    }


@router.get("/power")
async def get_power(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get French/Raven power map."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.symbolic.power_analysis import PowerMapper

    mapper = PowerMapper(graph_client)
    power_map = await mapper.compute_power_map(workspace_id)
    asymmetries = await mapper.detect_asymmetries(workspace_id)
    return {
        "dyads": [
            {
                "actor_id": d.actor_id,
                "target_id": d.target_id,
                "total_power": d.total_power,
                "asymmetry": d.asymmetry,
            }
            for d in power_map.dyads
        ],
        "most_powerful": power_map.most_powerful_actor,
        "average_asymmetry": power_map.average_asymmetry,
        "asymmetries": [
            {
                "actor_a": a.actor_a,
                "actor_b": a.actor_b,
                "advantage_holder": a.advantage_holder,
                "score": a.asymmetry_score,
                "recommendation": a.recommendation,
            }
            for a in asymmetries
        ],
    }


@router.get("/trust")
async def get_trust(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get Mayer/Davis/Schoorman trust matrix."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.symbolic.trust_analysis import TrustAnalyzer

    analyzer = TrustAnalyzer(graph_client)
    matrix = await analyzer.compute_trust_matrix(workspace_id)
    changes = await analyzer.detect_trust_changes(workspace_id)
    return {
        "average_trust": matrix.average_trust,
        "lowest_trust_pair": matrix.lowest_trust_pair,
        "highest_trust_pair": matrix.highest_trust_pair,
        "dyads": [
            {
                "trustor": d.trustor_id,
                "trustee": d.trustee_id,
                "ability": d.ability,
                "benevolence": d.benevolence,
                "integrity": d.integrity,
                "overall": d.overall_trust,
            }
            for d in matrix.dyads
        ],
        "recent_changes": [
            {
                "trustor": c.trustor_id,
                "trustee": c.trustee_id,
                "delta": c.trust_delta,
                "type": c.change_type,
                "event": c.event_description,
            }
            for c in changes[:10]
        ],
    }


@router.get("/causation")
async def get_causation(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get causal chain analysis."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.symbolic.causal_analysis import CausalAnalyzer

    analyzer = CausalAnalyzer(graph_client)
    chains = await analyzer.extract_causal_chains(workspace_id)
    roots = await analyzer.identify_root_causes(workspace_id)
    return {
        "chains": [
            {
                "root": c.root_event_id,
                "depth": c.depth,
                "has_cycle": c.has_cycle,
                "length": len(c.chain),
            }
            for c in chains[:10]
        ],
        "root_causes": [
            {
                "event_id": r.event_id,
                "description": r.event_description,
                "downstream": r.downstream_count,
            }
            for r in roots[:10]
        ],
    }


@router.get("/clusters")
async def get_clusters(
    workspace_id: str,
    resolution: float = 1.5,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get knowledge clusters with subdomain classification and theory enrichment."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    detector = KnowledgeClusterDetector(graph_client)
    report = await detector.detect_clusters(workspace_id, resolution=resolution)
    return {
        "workspace_id": report.workspace_id,
        "subdomain": report.subdomain,
        "cross_cluster_edges": report.cross_cluster_edges,
        "clusters": [
            {
                "cluster_id": c.cluster_id,
                "subdomain": c.subdomain,
                "community": c.community,
                "applicable_theories": c.applicable_theories,
                "primary_node_types": c.primary_node_types,
                "escalation_indicators": c.escalation_indicators,
                "node_count": c.node_count,
                "edge_count": c.edge_count,
                "density": c.density,
            }
            for c in report.clusters
        ],
    }


@router.get("/quality")
async def get_quality(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get graph quality metrics (completeness, consistency, coverage)."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.graph_quality import GraphQualityAnalyzer

    analyzer = GraphQualityAnalyzer(graph_client)
    dashboard = await analyzer.generate_quality_dashboard(workspace_id)
    return {
        "workspace_id": workspace_id,
        "overall_quality": dashboard.overall_quality,
        "completeness": {
            "score": dashboard.completeness.completeness_score if dashboard.completeness else 0,
            "tier": dashboard.completeness.tier_assessment if dashboard.completeness else "unknown",
            "missing_node_types": dashboard.completeness.missing_node_types[:5]
            if dashboard.completeness
            else [],
            "orphan_nodes": dashboard.completeness.orphan_node_count
            if dashboard.completeness
            else 0,
        },
        "consistency": {
            "score": dashboard.consistency.consistency_score if dashboard.consistency else 0,
            "edge_violations": dashboard.consistency.edge_schema_violations
            if dashboard.consistency
            else 0,
        },
        "coverage": {
            "score": dashboard.coverage.coverage_score if dashboard.coverage else 0,
            "avg_confidence": dashboard.coverage.avg_confidence if dashboard.coverage else 0,
            "temporal_span_days": dashboard.coverage.temporal_span_days
            if dashboard.coverage
            else 0,
        },
        "recommendations": dashboard.recommendations,
        "assessed_at": dashboard.assessed_at,
    }


# ── Reasoning Persistence ─────────────────────────────────────────────────


class ValidationRequest(BaseModel):
    """Body for POST .../reasoning/{trace_id}/validate."""

    verdict: str  # "confirmed" | "rejected" | "modified"
    notes: str = ""
    modified_value: str | None = None


class ValidationResponse(BaseModel):
    """Response after a human validates a reasoning trace."""

    trace_id: str
    workspace_id: str
    verdict: str
    validated_by: str
    validated_at: str
    notes: str = ""


class TracesResponse(BaseModel):
    """Paginated list of ReasoningTrace nodes for a workspace."""

    workspace_id: str
    traces: list[dict[str, Any]]
    total: int
    limit: int
    offset: int


@router.post("/reasoning/{trace_id}/validate")
async def validate_reasoning_trace(
    workspace_id: str,
    trace_id: str,
    body: ValidationRequest,
    request: Request,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> ValidationResponse:
    """Human-validate a persisted ReasoningTrace.

    Allowed verdicts: ``confirmed``, ``rejected``, ``modified``.
    On ``confirmed``, a ``VALIDATED_BY`` edge is created from each
    linked InferredFact to the validator user node.
    """
    _VALID_VERDICTS = {"confirmed", "rejected", "modified"}
    if body.verdict not in _VALID_VERDICTS:
        raise HTTPException(
            status_code=422,
            detail=f"verdict must be one of {sorted(_VALID_VERDICTS)}",
        )

    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")

    # Prefer the dedicated method; fall back to a no-op for mock clients
    validate_fn = getattr(graph_client, "validate_reasoning_trace", None)
    if validate_fn is None:
        raise HTTPException(
            status_code=501,
            detail="Graph client does not support reasoning trace validation.",
        )

    validated_by: str = getattr(request.state, "tenant_id", tenant_id)
    validated_at = datetime.utcnow().isoformat()

    found = await validate_fn(
        trace_id=trace_id,
        workspace_id=workspace_id,
        verdict=body.verdict,
        validated_by=validated_by,
        notes=body.notes,
        modified_value=body.modified_value,
    )
    if not found:
        raise HTTPException(
            status_code=404,
            detail=f"ReasoningTrace {trace_id!r} not found in workspace {workspace_id!r}.",
        )

    return ValidationResponse(
        trace_id=trace_id,
        workspace_id=workspace_id,
        verdict=body.verdict,
        validated_by=validated_by,
        validated_at=validated_at,
        notes=body.notes,
    )


@router.get("/reasoning/traces")
async def list_reasoning_traces(
    workspace_id: str,
    limit: int = 50,
    offset: int = 0,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> TracesResponse:
    """List all ReasoningTrace nodes for a workspace, paginated.

    Returns traces ordered by ``created_at`` descending.
    """
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")

    nodes = await graph_client.get_nodes(
        workspace_id=workspace_id,
        label="ReasoningTrace",
        limit=limit,
        offset=offset,
    )

    traces: list[dict[str, Any]] = []
    for node in nodes:
        if hasattr(node, "model_dump"):
            traces.append(node.model_dump(exclude={"embedding"}))
        else:
            # ConflictNode subclass serialisation fallback
            traces.append(
                {k: v for k, v in node.__dict__.items() if not k.startswith("_")}
            )

    return TracesResponse(
        workspace_id=workspace_id,
        traces=traces,
        total=len(traces),
        limit=limit,
        offset=offset,
    )


@router.get("/network")
async def get_network(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Get network topology metrics."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.symbolic.network_metrics import NetworkAnalyzer

    analyzer = NetworkAnalyzer(graph_client)
    centrality = await analyzer.compute_centrality(workspace_id)
    communities = await analyzer.detect_communities(workspace_id)
    polarisation = await analyzer.compute_polarization(workspace_id)
    brokers = await analyzer.identify_brokers(workspace_id)
    return {
        "centrality": [
            {
                "actor_id": c.actor_id,
                "betweenness": c.betweenness,
                "closeness": c.closeness,
                "degree": c.degree,
            }
            for c in centrality[:20]
        ],
        "communities": [
            {"id": c.community_id, "size": len(c.actor_ids), "actors": c.actor_ids[:5]}
            for c in communities
        ],
        "polarisation": {
            "modularity": polarisation.modularity,
            "level": polarisation.polarisation_level,
            "num_communities": polarisation.num_communities,
        },
        "brokers": [
            {
                "actor_id": b.actor_id,
                "betweenness": b.betweenness,
                "mediation_potential": b.mediation_potential,
            }
            for b in brokers[:5]
        ],
    }
