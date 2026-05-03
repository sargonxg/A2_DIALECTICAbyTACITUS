"""Dialectica text ingestion adapter for graph reasoning."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.graph_reasoning.schema import (
    EdgeKind,
    GraphReasoningEdge,
    GraphReasoningObject,
    ObjectKind,
    stable_edge_id,
    stable_object_id,
    utc_now,
)

_ACTOR_RE = re.compile(r"\b([A-Z][A-Za-z0-9&.'-]*(?:\s+[A-Z][A-Za-z0-9&.'-]*){0,4})\b")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_STOP_ACTORS = {
    "A",
    "An",
    "And",
    "But",
    "For",
    "If",
    "In",
    "It",
    "The",
    "This",
    "That",
    "They",
    "We",
}


@dataclass(frozen=True)
class AdaptedGraph:
    source_hash: str
    source_id: str
    episode_id: str
    objects: list[GraphReasoningObject]
    edges: list[GraphReasoningEdge]


class DialecticaIngestionAdapter:
    """Normalize text into provenance-bearing reasoning objects."""

    def adapt_text(
        self,
        *,
        text: str,
        workspace_id: str,
        tenant_id: str,
        source_title: str,
        source_uri: str | None,
        source_type: str,
        occurred_at: datetime | None = None,
    ) -> AdaptedGraph:
        normalized_text = text.strip()
        source_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
        source_id = f"source_{source_hash[:24]}"
        episode_id = f"episode_{source_hash[:24]}"
        now = utc_now()
        source = GraphReasoningObject(
            id=source_id,
            kind=ObjectKind.SOURCE,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            name=source_title,
            text=source_title,
            source_ids=[source_id],
            created_at=now,
            updated_at=now,
            valid_from=occurred_at,
            properties={
                "source_hash": source_hash,
                "source_uri": source_uri,
                "source_type": source_type,
                "length": len(normalized_text),
            },
        )
        evidence = GraphReasoningObject(
            id=stable_object_id(ObjectKind.EVIDENCE, workspace_id, normalized_text, [source_id]),
            kind=ObjectKind.EVIDENCE,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            name=source_title,
            text=normalized_text[:4000],
            description=f"Evidence extracted from {source_title}",
            source_ids=[source_id],
            created_at=now,
            updated_at=now,
            valid_from=occurred_at,
            properties={"source_hash": source_hash},
        )
        objects: dict[str, GraphReasoningObject] = {source.id: source, evidence.id: evidence}
        edges: dict[str, GraphReasoningEdge] = {}

        def add_object(obj: GraphReasoningObject) -> GraphReasoningObject:
            objects[obj.id] = obj
            return obj

        def add_edge(
            kind: EdgeKind,
            source_obj_id: str,
            target_obj_id: str,
            source_ids: list[str],
            confidence: float = 0.8,
            properties: dict | None = None,
        ) -> None:
            edge = GraphReasoningEdge(
                id=stable_edge_id(source_obj_id, target_obj_id, kind, source_ids, occurred_at),
                kind=kind,
                source_id=source_obj_id,
                target_id=target_obj_id,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                source_ids=source_ids,
                confidence=confidence,
                created_at=now,
                updated_at=now,
                valid_from=occurred_at,
                properties=properties or {},
            )
            edges[edge.id] = edge

        add_edge(EdgeKind.SOURCED_FROM, evidence.id, source.id, [source_id], 1.0)
        actors_by_name: dict[str, GraphReasoningObject] = {}
        sentences = [s.strip() for s in _SENTENCE_RE.split(normalized_text) if s.strip()]
        for sentence_index, sentence in enumerate(sentences):
            source_ids = [source_id, evidence.id]
            actor_names = self._extract_actor_names(sentence)
            active_actors: list[GraphReasoningObject] = []
            for actor_name in actor_names:
                actor = actors_by_name.get(actor_name.lower())
                if actor is None:
                    actor = add_object(
                        GraphReasoningObject(
                            id=stable_object_id(
                                ObjectKind.ACTOR, workspace_id, actor_name, source_ids
                            ),
                            kind=ObjectKind.ACTOR,
                            workspace_id=workspace_id,
                            tenant_id=tenant_id,
                            name=actor_name,
                            description=actor_name,
                            source_ids=source_ids,
                            confidence=0.72,
                            created_at=now,
                            updated_at=now,
                            valid_from=occurred_at,
                            properties={"extraction_method": "deterministic_capitalized_phrase"},
                        )
                    )
                    actors_by_name[actor_name.lower()] = actor
                    add_edge(EdgeKind.SOURCED_FROM, actor.id, evidence.id, source_ids, 0.9)
                active_actors.append(actor)

            claim = add_object(
                GraphReasoningObject(
                    id=stable_object_id(ObjectKind.CLAIM, workspace_id, sentence, source_ids),
                    kind=ObjectKind.CLAIM,
                    workspace_id=workspace_id,
                    tenant_id=tenant_id,
                    text=sentence,
                    description=sentence,
                    source_ids=source_ids,
                    confidence=0.68,
                    created_at=now,
                    updated_at=now,
                    valid_from=occurred_at,
                    properties={"sentence_index": sentence_index},
                )
            )
            add_edge(EdgeKind.EVIDENCES, evidence.id, claim.id, source_ids, 0.9)
            for actor in active_actors:
                add_edge(EdgeKind.MAKES_CLAIM, actor.id, claim.id, source_ids, 0.65)

            self._derive_typed_objects(
                sentence=sentence,
                sentence_index=sentence_index,
                occurred_at=occurred_at,
                source_ids=source_ids,
                actors=active_actors,
                claim=claim,
                add_object=add_object,
                add_edge=add_edge,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                now=now,
            )
        return AdaptedGraph(
            source_hash=source_hash,
            source_id=source_id,
            episode_id=episode_id,
            objects=list(objects.values()),
            edges=list(edges.values()),
        )

    def _extract_actor_names(self, sentence: str) -> list[str]:
        names = []
        for match in _ACTOR_RE.finditer(sentence):
            name = match.group(1).strip(" ,.;:")
            if len(name) >= 2 and name not in _STOP_ACTORS:
                names.append(name)
        return sorted(set(names))

    def _derive_typed_objects(
        self,
        *,
        sentence: str,
        sentence_index: int,
        occurred_at: datetime | None,
        source_ids: list[str],
        actors: list[GraphReasoningObject],
        claim: GraphReasoningObject,
        add_object: Callable[[GraphReasoningObject], GraphReasoningObject],
        add_edge: Callable[[EdgeKind, str, str, list[str], float, dict | None], None],
        workspace_id: str,
        tenant_id: str,
        now: datetime,
    ) -> None:
        lower = sentence.lower()
        typed_specs: list[tuple[ObjectKind, EdgeKind, float]] = []
        if any(token in lower for token in ("want", "wants", "seek", "seeks", "need", "needs")):
            typed_specs.append((ObjectKind.INTEREST, EdgeKind.HAS_INTEREST, 0.64))
        if any(
            token in lower
            for token in ("must", "cannot", "can't", "deadline", "blocked", "constraint")
        ):
            typed_specs.append((ObjectKind.CONSTRAINT, EdgeKind.HAS_CONSTRAINT, 0.66))
        if any(
            token in lower for token in ("leverage", "sanction", "control", "pressure", "influence")
        ):
            typed_specs.append((ObjectKind.LEVERAGE, EdgeKind.HAS_LEVERAGE, 0.63))
        if any(token in lower for token in ("commit", "committed", "agreed", "pledged", "will")):
            typed_specs.append((ObjectKind.COMMITMENT, EdgeKind.COMMITS_TO, 0.64))
        if any(
            token in lower
            for token in ("met", "signed", "announced", "protested", "attacked", "occurred")
        ):
            typed_specs.append((ObjectKind.EVENT, EdgeKind.PARTICIPATES_IN, 0.62))
        if any(
            token in lower for token in ("narrative", "frames", "claims that", "story", "blames")
        ):
            typed_specs.append((ObjectKind.NARRATIVE, EdgeKind.PROMOTES, 0.6))

        for kind, edge_kind, confidence in typed_specs:
            obj = add_object(
                GraphReasoningObject(
                    id=stable_object_id(kind, workspace_id, sentence, source_ids),
                    kind=kind,
                    workspace_id=workspace_id,
                    tenant_id=tenant_id,
                    text=sentence,
                    description=sentence,
                    source_ids=source_ids,
                    confidence=confidence,
                    created_at=now,
                    updated_at=now,
                    valid_from=occurred_at,
                    properties={"sentence_index": sentence_index},
                )
            )
            add_edge(EdgeKind.EVIDENCES, claim.id, obj.id, source_ids, confidence, None)
            for actor in actors:
                add_edge(edge_kind, actor.id, obj.id, source_ids, confidence, None)
