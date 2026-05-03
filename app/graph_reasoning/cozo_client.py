"""CozoDB reasoning mirror."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from app.graph_reasoning.schema import GraphReasoningEdge, GraphReasoningObject, ObjectKind

logger = logging.getLogger(__name__)

RELATION_NAMES = (
    "actor",
    "claim",
    "constraint",
    "leverage",
    "commitment",
    "event",
    "narrative",
    "source",
    "evidence",
    "edge",
)


class CozoReasoningClient:
    """Read-optimized reasoning mirror with Cozo-compatible relation names."""

    def __init__(self, snapshot_path: str | None = None) -> None:
        self.snapshot_path = snapshot_path or os.getenv("COZO_SNAPSHOT_PATH", "")
        self.mode = "memory"
        self._objects: dict[str, dict[str, Any]] = {}
        self._edges: dict[str, dict[str, Any]] = {}
        self._db: Any | None = None
        self._try_native()
        self.load_snapshot()

    def _try_native(self) -> None:
        if os.getenv("COZO_USE_EMBEDDED", "false").lower() != "true":
            return
        try:
            from cozo_embedded import CozoDbPy  # type: ignore

            self._db = CozoDbPy(
                os.getenv("COZO_ENGINE", "mem"),
                os.getenv("COZO_PATH", ""),
                os.getenv("COZO_OPTIONS", "{}"),
            )
            self.mode = "embedded"
        except Exception as exc:
            logger.warning("cozo-embedded unavailable, using memory mirror: %s", exc)
            self.mode = "memory"

    async def initialize(self) -> None:
        if self._db is None:
            return
        try:
            for relation in RELATION_NAMES:
                self._run_native(f":create {relation} {{id: String => payload: Json}}")
        except Exception as exc:
            logger.info("Cozo relation initialization skipped or already complete: %s", exc)

    async def health(self) -> dict[str, str]:
        return {
            "status": "up",
            "mode": self.mode,
            "details": f"{len(self._objects)} objects, {len(self._edges)} edges mirrored",
        }

    async def upsert_objects(self, objects: list[GraphReasoningObject]) -> list[str]:
        for obj in objects:
            payload = obj.model_dump(mode="json")
            payload["relation"] = _relation_for_kind(str(obj.kind))
            self._objects[obj.id] = payload
            self._put_native(payload["relation"], obj.id, payload)
        self.save_snapshot()
        return [obj.id for obj in objects]

    async def upsert_edges(self, edges: list[GraphReasoningEdge]) -> list[str]:
        for edge in edges:
            payload = edge.model_dump(mode="json")
            payload["relation"] = "edge"
            self._edges[edge.id] = payload
            self._put_native("edge", edge.id, payload)
        self.save_snapshot()
        return [edge.id for edge in edges]

    async def mirror_payload(self, payload: dict[str, list[dict[str, Any]]]) -> None:
        for obj in payload.get("objects", []):
            if obj.get("id"):
                obj["relation"] = _relation_for_kind(str(obj.get("kind", "")))
                self._objects[obj["id"]] = obj
                self._put_native(obj["relation"], obj["id"], obj)
        for edge in payload.get("edges", []):
            if edge.get("id"):
                edge["relation"] = "edge"
                self._edges[edge["id"]] = edge
                self._put_native("edge", edge["id"], edge)
        self.save_snapshot()

    def get_object(self, object_id: str) -> dict[str, Any] | None:
        return self._objects.get(object_id)

    def objects_by_kind(
        self, kind: ObjectKind | str, workspace_id: str | None = None
    ) -> list[dict[str, Any]]:
        kind_value = str(kind)
        return [
            obj
            for obj in self._objects.values()
            if str(obj.get("kind")) == kind_value
            and (workspace_id is None or obj.get("workspace_id") == workspace_id)
        ]

    def edges_for(self, object_id: str, workspace_id: str | None = None) -> list[dict[str, Any]]:
        return [
            edge
            for edge in self._edges.values()
            if (edge.get("source_id") == object_id or edge.get("target_id") == object_id)
            and (workspace_id is None or edge.get("workspace_id") == workspace_id)
        ]

    def changed_since(
        self, timestamp: str, workspace_id: str | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        objects = [
            obj
            for obj in self._objects.values()
            if str(obj.get("updated_at", obj.get("created_at", ""))) >= timestamp
            and (workspace_id is None or obj.get("workspace_id") == workspace_id)
        ]
        edges = [
            edge
            for edge in self._edges.values()
            if str(edge.get("updated_at", edge.get("created_at", ""))) >= timestamp
            and (workspace_id is None or edge.get("workspace_id") == workspace_id)
        ]
        return {"objects": objects, "edges": edges}

    def timeline(
        self,
        actor_ids: list[str],
        start: str | None = None,
        end: str | None = None,
        workspace_id: str | None = None,
    ) -> list[dict[str, Any]]:
        actor_set = set(actor_ids)
        related_event_ids = {
            edge["target_id"]
            for edge in self._edges.values()
            if edge.get("source_id") in actor_set
            and edge.get("kind") == "PARTICIPATES_IN"
            and (workspace_id is None or edge.get("workspace_id") == workspace_id)
        }
        events = []
        for obj in self._objects.values():
            if obj.get("kind") != "Event":
                continue
            if actor_set and obj.get("id") not in related_event_ids:
                continue
            if workspace_id and obj.get("workspace_id") != workspace_id:
                continue
            ts = str(obj.get("valid_from") or obj.get("created_at") or "")
            if start and ts < start:
                continue
            if end and ts > end:
                continue
            events.append(obj)
        return sorted(
            events, key=lambda item: str(item.get("valid_from") or item.get("created_at") or "")
        )

    def relation_counts(self) -> dict[str, int]:
        counts = dict.fromkeys(RELATION_NAMES, 0)
        for obj in self._objects.values():
            relation = obj.get("relation", "")
            counts[relation] = counts.get(relation, 0) + 1
        counts["edge"] = len(self._edges)
        return counts

    def native_relation(self, relation: str) -> list[dict[str, Any]]:
        """Return raw rows from an embedded Cozo relation when available."""
        if self._db is None:
            return []
        result = self._run_native(f"?[id, payload] := *{relation}[id, payload]")
        return [{"id": row[0], "payload": row[1]} for row in result.get("rows", [])]

    def _run_native(self, script: str) -> dict[str, Any]:
        if self._db is None:
            return {"headers": [], "rows": []}
        return self._db.run_script(script, {}, False)

    def _put_native(self, relation: str, item_id: str, payload: dict[str, Any]) -> None:
        if self._db is None or relation not in RELATION_NAMES:
            return
        try:
            self._db.run_script(
                f"?[id, payload] <- [[$id, $payload]] :put {relation} {{id => payload}}",
                {"id": item_id, "payload": payload},
                False,
            )
        except Exception as exc:
            logger.warning("Cozo native put failed for %s/%s: %s", relation, item_id, exc)

    def save_snapshot(self) -> None:
        if not self.snapshot_path:
            return
        try:
            path = Path(self.snapshot_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"objects": self._objects, "edges": self._edges}, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("Cozo snapshot save failed: %s", exc)

    def load_snapshot(self) -> None:
        if not self.snapshot_path:
            return
        path = Path(self.snapshot_path)
        if not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self._objects.update(payload.get("objects", {}))
            self._edges.update(payload.get("edges", {}))
        except Exception as exc:
            logger.warning("Cozo snapshot load failed: %s", exc)


def _relation_for_kind(kind: str) -> str:
    return {
        "Actor": "actor",
        "Claim": "claim",
        "Constraint": "constraint",
        "Leverage": "leverage",
        "Commitment": "commitment",
        "Event": "event",
        "Narrative": "narrative",
        "Source": "source",
        "Evidence": "evidence",
    }.get(kind, "object")
