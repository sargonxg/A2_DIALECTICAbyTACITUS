"""Deterministic local primitive extraction.

This is a real fallback extractor, not a fake AI response. It extracts obvious
actors, commitments, constraints, narratives, claims, events, and actor states
from source text using transparent heuristics. LLM-backed extraction can replace
this module later while preserving the same Pydantic output contract.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import UTC, datetime

from dialectica.ontology.models import (
    Actor,
    ActorState,
    Claim,
    Commitment,
    Constraint,
    Episode,
    Event,
    EvidenceSpan,
    ExtractionRun,
    GraphPrimitive,
    Narrative,
    SourceChunk,
)

ACTOR_PATTERN = re.compile(
    r"\b(?:Actor|Party|State|Ministry|Union|Agency|Mediator|Mayor|Finance Office|Alex|Sam|"
    r"Parent|Teen)\s+[A-Z]?\w*|\b(?:Alex|Sam|Parent|Teen|State A|State B|Mayor|"
    r"Finance Office|Agency)\b"
)
COMMITMENT_PATTERN = re.compile(
    r"\b(agree[ds]?|commit(?:ted)?|promise[ds]?|pledge[ds]?|will|shall|lock it in)\b",
    re.I,
)
CONSTRAINT_PATTERN = re.compile(
    r"\b(only after|cannot|must|deadline|expires|red line|requires|constrain|"
    r"penalt(?:y|ies)|limited)\b",
    re.I,
)
NARRATIVE_PATTERN = re.compile(
    r"\b(says|claims|argues|warns|citing|you never|this is about|just want)\b", re.I
)
EVENT_PATTERN = re.compile(
    r"\b(after|then|announced|suspended|postponed|delayed|failed|walkout|meeting|inspection)\b",
    re.I,
)
LEVERAGE_PATTERN = re.compile(
    r"\b(power|leverage|capacity|funds|tariffs|penalties|authority|control)\b", re.I
)
TRUST_PATTERN = re.compile(r"\b(trust|distrust|confidence|guarantee|safety)\b", re.I)


def _sentence_spans(text: str) -> Iterable[tuple[str, int, int]]:
    for match in re.finditer(r"[^.!?\n]+[.!?\n]?", text):
        sentence = match.group(0).strip()
        if sentence:
            yield sentence, match.start(), match.end()


def _span_for(
    chunk: SourceChunk,
    sentence: str,
    start: int,
    end: int,
    *,
    extraction_run_id: str,
    confidence: float,
) -> EvidenceSpan:
    return EvidenceSpan(
        workspace_id=chunk.workspace_id,
        case_id=chunk.case_id,
        source_id=chunk.source_id,
        chunk_id=chunk.id,
        extraction_run_id=extraction_run_id,
        provenance_span=sentence,
        start_char=chunk.start_char + start,
        end_char=chunk.start_char + end,
        confidence=confidence,
    )


def extract_primitives(
    chunks: list[SourceChunk],
    *,
    extraction_run: ExtractionRun,
    case_id: str,
    episode_name: str = "Initial episode",
) -> list[GraphPrimitive]:
    primitives: list[GraphPrimitive] = [extraction_run]
    actor_by_name: dict[str, Actor] = {}
    episode = Episode(
        workspace_id=extraction_run.workspace_id,
        case_id=case_id,
        name=episode_name,
        objective="Understand conflict primitives from source documents",
        source_id=chunks[0].source_id if chunks else "",
        extraction_run_id=extraction_run.id,
        confidence=1.0,
    )
    primitives.append(episode)

    for chunk in chunks:
        primitives.append(chunk)
        for sentence, start, end in _sentence_spans(chunk.text):
            actors = sorted({match.group(0).strip() for match in ACTOR_PATTERN.finditer(sentence)})
            evidence = _span_for(
                chunk,
                sentence,
                start,
                end,
                extraction_run_id=extraction_run.id,
                confidence=0.72,
            )
            primitives.append(evidence)

            for actor_name in actors:
                if actor_name not in actor_by_name:
                    organization_terms = ["Ministry", "Union", "Agency", "Office"]
                    actor = Actor(
                        workspace_id=chunk.workspace_id,
                        case_id=chunk.case_id,
                        source_id=chunk.source_id,
                        extraction_run_id=extraction_run.id,
                        evidence_span_id=evidence.id,
                        provenance_span=sentence,
                        confidence=0.74,
                        name=actor_name,
                        actor_type=(
                            "organization"
                            if any(term in actor_name for term in organization_terms)
                            else "person_or_collective"
                        ),
                    )
                    actor_by_name[actor_name] = actor
                    primitives.append(actor)

            primary_actor = actor_by_name.get(actors[0]) if actors else None

            if COMMITMENT_PATTERN.search(sentence) and primary_actor:
                primitives.append(
                    Commitment(
                        workspace_id=chunk.workspace_id,
                        case_id=chunk.case_id,
                        episode_id=episode.id,
                        source_id=chunk.source_id,
                        extraction_run_id=extraction_run.id,
                        evidence_span_id=evidence.id,
                        provenance_span=sentence,
                        confidence=0.7,
                        observed_at=datetime.now(UTC),
                        actor_id=primary_actor.id,
                        description=sentence,
                        commitment_status="candidate",
                        constrains_actor_id=primary_actor.id,
                    )
                )

            if CONSTRAINT_PATTERN.search(sentence):
                primitives.append(
                    Constraint(
                        workspace_id=chunk.workspace_id,
                        case_id=chunk.case_id,
                        episode_id=episode.id,
                        source_id=chunk.source_id,
                        extraction_run_id=extraction_run.id,
                        evidence_span_id=evidence.id,
                        provenance_span=sentence,
                        confidence=0.72,
                        actor_id=primary_actor.id if primary_actor else None,
                        description=sentence,
                        constraint_type="temporal_or_policy",
                    )
                )

            if EVENT_PATTERN.search(sentence):
                primitives.append(
                    Event(
                        workspace_id=chunk.workspace_id,
                        case_id=chunk.case_id,
                        episode_id=episode.id,
                        source_id=chunk.source_id,
                        extraction_run_id=extraction_run.id,
                        evidence_span_id=evidence.id,
                        provenance_span=sentence,
                        confidence=0.68,
                        description=sentence,
                        event_type="reported_change",
                    )
                )

            if NARRATIVE_PATTERN.search(sentence):
                primitives.append(
                    Narrative(
                        workspace_id=chunk.workspace_id,
                        case_id=chunk.case_id,
                        episode_id=episode.id,
                        source_id=chunk.source_id,
                        extraction_run_id=extraction_run.id,
                        evidence_span_id=evidence.id,
                        provenance_span=sentence,
                        confidence=0.66,
                        actor_id=primary_actor.id if primary_actor else None,
                        content=sentence,
                        narrative_type="reported_frame",
                    )
                )

            if sentence:
                primitives.append(
                    Claim(
                        workspace_id=chunk.workspace_id,
                        case_id=chunk.case_id,
                        episode_id=episode.id,
                        source_id=chunk.source_id,
                        extraction_run_id=extraction_run.id,
                        evidence_span_id=evidence.id,
                        provenance_span=sentence,
                        confidence=0.64,
                        text=sentence,
                        claim_status="extracted",
                        assertion_type="explicit",
                        subject_actor_id=primary_actor.id if primary_actor else None,
                    )
                )

            has_state_signal = LEVERAGE_PATTERN.search(sentence) or TRUST_PATTERN.search(sentence)
            if primary_actor and has_state_signal:
                primitives.append(
                    ActorState(
                        workspace_id=chunk.workspace_id,
                        case_id=chunk.case_id,
                        episode_id=episode.id,
                        source_id=chunk.source_id,
                        extraction_run_id=extraction_run.id,
                        evidence_span_id=evidence.id,
                        provenance_span=sentence,
                        confidence=0.62,
                        actor_id=primary_actor.id,
                        leverage_level="mentioned" if LEVERAGE_PATTERN.search(sentence) else None,
                        trust_level="mentioned" if TRUST_PATTERN.search(sentence) else None,
                        source_ids=[chunk.source_id],
                    )
                )

    return primitives
