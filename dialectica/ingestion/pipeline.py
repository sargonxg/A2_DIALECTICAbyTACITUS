"""End-to-end local ingestion pipeline."""

from __future__ import annotations

from pathlib import Path

from dialectica.ingestion.chunk_documents import chunk_documents
from dialectica.ingestion.extract_primitives import extract_primitives
from dialectica.ingestion.load_documents import load_documents
from dialectica.ingestion.map_to_ontology import validate_core_mappings
from dialectica.ontology.models import ExtractionRun, GraphPrimitive


def ingest_path(
    path: str | Path,
    *,
    workspace_id: str,
    case_id: str,
    model_name: str = "local-rule-extractor",
    extraction_method: str = "rule_based",
    chunk_chars: int = 1800,
) -> list[GraphPrimitive]:
    extraction_run = ExtractionRun(
        workspace_id=workspace_id,
        case_id=case_id,
        model_name=model_name,
        extraction_method=extraction_method,
    )
    loaded = load_documents(path, workspace_id=workspace_id, case_id=case_id)
    chunks = chunk_documents(
        loaded,
        extraction_run_id=extraction_run.id,
        chunk_chars=chunk_chars,
    )
    primitives: list[GraphPrimitive] = []
    for item in loaded:
        primitives.append(item.document)
    primitives.extend(
        extract_primitives(
            chunks,
            extraction_run=extraction_run,
            case_id=case_id,
            episode_name=f"{case_id} initial episode",
        )
    )
    errors = validate_core_mappings(primitives)
    if errors:
        raise ValueError("; ".join(errors))
    return primitives
