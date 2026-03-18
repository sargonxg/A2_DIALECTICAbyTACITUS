"""
Benchmark Router — Extraction pipeline evaluation endpoints.

Admin-only endpoints for running benchmark evaluations against gold-standard
annotated corpora. Measures precision, recall, and F1 for node extraction,
edge extraction, and graph-augmented structural accuracy.
"""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from dialectica_api.deps import require_admin
from dialectica_api.benchmark_runner import (
    BenchmarkRunner,
    VALID_CORPUS_IDS,
)

router = APIRouter(prefix="/v1/admin/benchmark", tags=["benchmark"])

# In-memory benchmark history store
_benchmark_history: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class CorpusId(StrEnum):
    jcpoa = "jcpoa"
    romeo_juliet = "romeo_juliet"
    crime_punishment = "crime_punishment"
    war_peace = "war_peace"
    custom = "custom"


class BenchmarkTier(StrEnum):
    essential = "essential"
    standard = "standard"
    full = "full"


class BenchmarkRunRequest(BaseModel):
    """Request body for POST /run."""
    corpus_id: CorpusId = CorpusId.jcpoa
    custom_text: str | None = None
    custom_gold: dict[str, Any] | None = None
    tier: BenchmarkTier = BenchmarkTier.standard
    model: str = "gemini-2.0-flash"
    include_graph_augmented: bool = False


class MetricScoreResponse(BaseModel):
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0


class BenchmarkResultsResponse(BaseModel):
    overall: MetricScoreResponse
    by_node_type: dict[str, MetricScoreResponse] = Field(default_factory=dict)
    by_edge_type: dict[str, MetricScoreResponse] = Field(default_factory=dict)
    graph_augmented: MetricScoreResponse | None = None
    evaluation_points: int = 480
    extraction_time_ms: float = 0.0
    hallucination_rate: float = 0.0


class BenchmarkRunResponse(BaseModel):
    benchmark_id: str
    corpus_id: str
    tier: str
    model: str
    results: BenchmarkResultsResponse
    completed_at: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _metric_to_response(m: Any) -> MetricScoreResponse:
    return MetricScoreResponse(
        precision=m.precision,
        recall=m.recall,
        f1=m.f1,
        true_positives=m.true_positives,
        false_positives=m.false_positives,
        false_negatives=m.false_negatives,
    )


def _result_to_response(result: Any) -> BenchmarkRunResponse:
    r = result.results
    return BenchmarkRunResponse(
        benchmark_id=result.benchmark_id,
        corpus_id=result.corpus_id,
        tier=result.tier,
        model=result.model,
        results=BenchmarkResultsResponse(
            overall=_metric_to_response(r.overall),
            by_node_type={k: _metric_to_response(v) for k, v in r.by_node_type.items()},
            by_edge_type={k: _metric_to_response(v) for k, v in r.by_edge_type.items()},
            graph_augmented=_metric_to_response(r.graph_augmented) if r.graph_augmented else None,
            evaluation_points=r.evaluation_points,
            extraction_time_ms=r.extraction_time_ms,
            hallucination_rate=r.hallucination_rate,
        ),
        completed_at=result.completed_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/run", response_model=BenchmarkRunResponse)
async def run_benchmark(
    body: BenchmarkRunRequest,
    _admin: None = Depends(require_admin),
) -> BenchmarkRunResponse:
    """Run benchmark evaluation against a gold-standard annotated corpus.

    Extracts a conflict graph from the corpus source text, compares it
    against the gold-standard annotation, and returns precision/recall/F1
    scores broken down by node type and edge type.
    """
    runner = BenchmarkRunner()

    try:
        result = await runner.run_benchmark(
            corpus_id=body.corpus_id.value,
            tier=body.tier.value,
            model=body.model,
            include_graph_augmented=body.include_graph_augmented,
            custom_text=body.custom_text,
            custom_gold=body.custom_gold,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    response = _result_to_response(result)

    # Persist to in-memory history
    _benchmark_history[result.benchmark_id] = response.model_dump()

    return response


@router.get("/history", response_model=list[BenchmarkRunResponse])
async def list_benchmark_history(
    _admin: None = Depends(require_admin),
    limit: int = 50,
    offset: int = 0,
) -> list[BenchmarkRunResponse]:
    """List past benchmark runs, most recent first."""
    items = list(_benchmark_history.values())
    items.reverse()
    page = items[offset : offset + limit]
    return [BenchmarkRunResponse(**item) for item in page]


@router.get("/{benchmark_id}", response_model=BenchmarkRunResponse)
async def get_benchmark_run(
    benchmark_id: str,
    _admin: None = Depends(require_admin),
) -> BenchmarkRunResponse:
    """Get details of a specific benchmark run."""
    item = _benchmark_history.get(benchmark_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark run '{benchmark_id}' not found.",
        )
    return BenchmarkRunResponse(**item)
