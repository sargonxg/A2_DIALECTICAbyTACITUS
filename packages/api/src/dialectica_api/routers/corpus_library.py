"""
Corpus Library Router — list ingested SourceDocuments per workspace.

Backed by the same in-process JobStore as the extraction endpoints. Each
completed extraction job persists a SourceDocument summary onto the job;
this endpoint surfaces those summaries in a stable shape so the
``/workspaces/[id]/corpus`` UI can render them.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dialectica_api.deps import get_current_tenant
from dialectica_api.services.job_store import JobStore, get_job_store

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["corpus"])


class SourceDocumentSummary(BaseModel):
    id: str
    title: str
    content_hash: str
    word_count: int
    language: str = "en"
    ingested_at: str
    extraction_tier: str
    extraction_model: str
    nodes_extracted: int
    edges_extracted: int
    errors: int
    job_id: str
    source_kind: str
    gutenberg_book_id: str | None = None


class CorpusLibraryResponse(BaseModel):
    workspace_id: str
    total_documents: int
    total_words: int
    total_nodes: int
    total_edges: int
    documents: list[SourceDocumentSummary]


@router.get("/corpus/documents", response_model=CorpusLibraryResponse)
async def list_corpus_documents(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    store: JobStore = Depends(get_job_store),  # noqa: B008
) -> CorpusLibraryResponse:
    """List ingested SourceDocuments for this workspace."""
    docs: list[SourceDocumentSummary] = []
    total_words = 0
    total_nodes = 0
    total_edges = 0

    for job in store.list_jobs(workspace_id=workspace_id):
        if job.get("status") != "complete":
            continue
        sd: dict[str, Any] | None = job.get("source_document")
        if not sd:
            continue
        docs.append(
            SourceDocumentSummary(
                id=sd.get("id", job["job_id"]),
                title=sd.get("title", ""),
                content_hash=sd.get("content_hash", ""),
                word_count=sd.get("word_count", 0),
                language=sd.get("language", "en"),
                ingested_at=sd.get("ingested_at", job.get("created_at", "")),
                extraction_tier=sd.get("extraction_tier", "standard"),
                extraction_model=sd.get("extraction_model", "gemini-2.5-flash"),
                nodes_extracted=sd.get("nodes_extracted", job.get("nodes_extracted", 0)),
                edges_extracted=sd.get("edges_extracted", job.get("edges_extracted", 0)),
                errors=sd.get("errors", 0),
                job_id=job["job_id"],
                source_kind=job.get("source_kind", "text"),
                gutenberg_book_id=job.get("gutenberg_book_id"),
            )
        )
        total_words += sd.get("word_count", 0)
        total_nodes += sd.get("nodes_extracted", 0)
        total_edges += sd.get("edges_extracted", 0)

    docs.sort(key=lambda d: d.ingested_at, reverse=True)

    return CorpusLibraryResponse(
        workspace_id=workspace_id,
        total_documents=len(docs),
        total_words=total_words,
        total_nodes=total_nodes,
        total_edges=total_edges,
        documents=docs,
    )
