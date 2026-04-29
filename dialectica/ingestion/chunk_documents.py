"""Chunk documents while preserving source offsets."""

from __future__ import annotations

from dialectica.ingestion.load_documents import LoadedDocument
from dialectica.ontology.models import SourceChunk


def chunk_document(
    loaded: LoadedDocument,
    *,
    extraction_run_id: str,
    chunk_chars: int = 1800,
    overlap: int = 150,
) -> list[SourceChunk]:
    if chunk_chars <= overlap:
        raise ValueError("chunk_chars must be greater than overlap")

    chunks: list[SourceChunk] = []
    text = loaded.text
    start = 0
    index = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        if end < len(text):
            boundary = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
            if boundary > start + 200:
                end = boundary + 1
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                SourceChunk(
                    workspace_id=loaded.document.workspace_id,
                    case_id=loaded.document.case_id,
                    source_id=loaded.document.source_id,
                    document_id=loaded.document.id,
                    chunk_index=index,
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                    extraction_run_id=extraction_run_id,
                )
            )
            index += 1
        start = end - overlap if end < len(text) else len(text)
    return chunks


def chunk_documents(
    loaded_documents: list[LoadedDocument],
    *,
    extraction_run_id: str,
    chunk_chars: int = 1800,
    overlap: int = 150,
) -> list[SourceChunk]:
    chunks: list[SourceChunk] = []
    for loaded in loaded_documents:
        chunks.extend(
            chunk_document(
                loaded,
                extraction_run_id=extraction_run_id,
                chunk_chars=chunk_chars,
                overlap=overlap,
            )
        )
    return chunks
