"""Pre-ingestion pipeline utilities for large text and dynamic ontology."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.graph_reasoning.schema import ObjectKind, stable_hash

CORE_NODE_TYPES = [
    ObjectKind.ACTOR.value,
    ObjectKind.CLAIM.value,
    ObjectKind.INTEREST.value,
    ObjectKind.CONSTRAINT.value,
    ObjectKind.LEVERAGE.value,
    ObjectKind.COMMITMENT.value,
    ObjectKind.EVENT.value,
    ObjectKind.NARRATIVE.value,
    ObjectKind.SOURCE.value,
    ObjectKind.EVIDENCE.value,
]


@dataclass(frozen=True)
class SourceChunk:
    id: str
    label: str
    text: str
    start_char: int
    end_char: int
    ordinal: int
    reason: str


@dataclass(frozen=True)
class PipelinePlan:
    original_text: str
    cleaned_text: str
    removed_sections: list[str]
    chunks: list[SourceChunk]
    objective: str
    ontology_profile: str
    dynamic_ontology: dict

    def summary(self) -> dict:
        return {
            "original_chars": len(self.original_text),
            "cleaned_chars": len(self.cleaned_text),
            "removed_sections": self.removed_sections,
            "chunk_count": len(self.chunks),
            "chunking_strategy": "heading_or_size_window",
            "objective": self.objective,
            "ontology_profile": self.ontology_profile,
            "dynamic_ontology": self.dynamic_ontology,
            "stages": [
                "source_cleaning",
                "chunking",
                "dynamic_ontology_mapping",
                "graphiti_episode",
                "neo4j_upsert",
                "cozo_mirror",
                "cloud_sql_audit",
            ],
        }


def build_pipeline_plan(
    *,
    text: str,
    workspace_id: str,
    objective: str = "",
    ontology_profile: str = "human-friction",
    chunk_chars: int = 6000,
) -> PipelinePlan:
    cleaned_text, removed = clean_source_text(text)
    chunks = chunk_text(cleaned_text, workspace_id=workspace_id, chunk_chars=chunk_chars)
    ontology = build_dynamic_ontology(objective=objective, ontology_profile=ontology_profile)
    return PipelinePlan(
        original_text=text,
        cleaned_text=cleaned_text,
        removed_sections=removed,
        chunks=chunks,
        objective=objective,
        ontology_profile=ontology_profile,
        dynamic_ontology=ontology,
    )


def clean_source_text(text: str) -> tuple[str, list[str]]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    removed: list[str] = []

    start_marker = re.search(
        r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*",
        cleaned,
        flags=re.IGNORECASE,
    )
    if start_marker:
        cleaned = cleaned[start_marker.end() :]
        removed.append("project_gutenberg_header")

    end_marker = re.search(
        r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*",
        cleaned,
        flags=re.IGNORECASE,
    )
    if end_marker:
        cleaned = cleaned[: end_marker.start()]
        removed.append("project_gutenberg_footer")

    cleaned = re.sub(
        r"^(?:Produced by|Transcribed from|This eBook is for the use of).*$",
        "",
        cleaned,
        flags=re.I | re.M,
    )
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return (cleaned or text.strip(), removed)


def chunk_text(text: str, *, workspace_id: str, chunk_chars: int = 6000) -> list[SourceChunk]:
    chunk_chars = max(1000, chunk_chars)
    headings = list(
        re.finditer(
            r"^(ACT\s+[IVXLC]+|SCENE\s+[IVXLC]+|CHAPTER\s+\d+|CHAPTER\s+[IVXLC]+|BOOK\s+[A-ZIVXLC]+|SECTION\s+\d+)\b[^\n]*",
            text,
            flags=re.I | re.M,
        )
    )
    chunks: list[SourceChunk] = []
    if headings:
        for index, match in enumerate(headings):
            start = match.start()
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            for sub_index, window in enumerate(_window_text(text[start:end], chunk_chars)):
                window_start = start + window[0]
                window_end = start + window[1]
                chunks.append(
                    _chunk(
                        workspace_id,
                        len(chunks),
                        str(match.group(0)).strip()[:80],
                        text[window_start:window_end].strip(),
                        window_start,
                        window_end,
                        "heading_window" if sub_index else "explicit_heading",
                    )
                )
        return chunks

    for start, end in _window_text(text, chunk_chars):
        chunks.append(
            _chunk(
                workspace_id,
                len(chunks),
                f"Chunk {len(chunks) + 1}",
                text[start:end].strip(),
                start,
                end,
                "size_window",
            )
        )
    return chunks or [
        _chunk(workspace_id, 0, "Chunk 1", text.strip(), 0, len(text), "single_chunk")
    ]


def build_dynamic_ontology(*, objective: str, ontology_profile: str) -> dict:
    profile = ontology_profile or "human-friction"
    mappings = _profile_mappings(profile)
    required = sorted({mapping["core_mapping"] for mapping in mappings} | set(CORE_NODE_TYPES))
    return {
        "id": f"ontology_{stable_hash(profile, objective, length=16)}",
        "profile_id": profile,
        "objective": objective,
        "core_nodes": CORE_NODE_TYPES,
        "required_nodes": required,
        "custom_mappings": mappings,
        "passes": [
            {
                "id": "pre_ingestion",
                "purpose": "Clean, chunk, license-tag, and source-hash material before extraction.",
            },
            {
                "id": "primitive_extraction",
                "purpose": "Extract only canonical graph objects with evidence and timestamps.",
            },
            {
                "id": "post_ingestion",
                "purpose": (
                    "Write Neo4j, record Graphiti episode, mirror Cozo, "
                    "and audit Cloud SQL."
                ),
            },
        ],
        "validation_rules": [
            "Every object and edge must carry source_ids.",
            "Every claim-like object must link to Source or Evidence.",
            "Custom ontology labels must map back to a canonical core node.",
            "Cozo is a rebuildable mirror and never the primary graph store.",
        ],
    }


def _window_text(text: str, chunk_chars: int) -> list[tuple[int, int]]:
    windows: list[tuple[int, int]] = []
    start = 0
    while start < len(text):
        hard_end = min(start + chunk_chars, len(text))
        if hard_end == len(text):
            end = hard_end
        else:
            sentence_end = max(
                text.rfind(". ", start, hard_end),
                text.rfind("\n\n", start, hard_end),
            )
            end = sentence_end + 1 if sentence_end > start + (chunk_chars // 2) else hard_end
        windows.append((start, end))
        start = end
    return windows


def _chunk(
    workspace_id: str,
    ordinal: int,
    label: str,
    text: str,
    start_char: int,
    end_char: int,
    reason: str,
) -> SourceChunk:
    return SourceChunk(
        id=f"chunk_{stable_hash(workspace_id, ordinal, start_char, end_char, text[:200])}",
        label=label,
        text=text,
        start_char=start_char,
        end_char=end_char,
        ordinal=ordinal,
        reason=reason,
    )


def _profile_mappings(profile: str) -> list[dict[str, str]]:
    if profile == "policy-analysis":
        return [
            {
                "custom_type": "Institution",
                "core_mapping": "Actor",
                "purpose": "Agency or stakeholder body.",
            },
            {
                "custom_type": "StatutoryRule",
                "core_mapping": "Constraint",
                "purpose": "Legal or procedural limit.",
            },
            {
                "custom_type": "VetoPoint",
                "core_mapping": "Leverage",
                "purpose": "Capacity to block or approve.",
            },
        ]
    if profile == "literary-conflict":
        return [
            {
                "custom_type": "Character",
                "core_mapping": "Actor",
                "purpose": "Person or group in a narrative conflict.",
            },
            {
                "custom_type": "Scene",
                "core_mapping": "Event",
                "purpose": "Bounded narrative action window.",
            },
            {
                "custom_type": "FeudFrame",
                "core_mapping": "Narrative",
                "purpose": "Identity or legitimacy frame.",
            },
        ]
    return [
        {
            "custom_type": "Participant",
            "core_mapping": "Actor",
            "purpose": "Person, group, institution, or role.",
        },
        {
            "custom_type": "Assertion",
            "core_mapping": "Claim",
            "purpose": "Source-backed statement.",
        },
        {
            "custom_type": "FrictionPoint",
            "core_mapping": "Constraint",
            "purpose": "Limit, blocker, rule, or deadline.",
        },
    ]
