"""
ACLED Connector — Armed Conflict Location & Event Data Project.

OAuth REST client for https://api.acleddata.com/acled/read.
Maps ACLED events to ACO Event/Actor nodes with severity scaling.
"""

from __future__ import annotations

import contextlib
import logging
import os
from datetime import datetime
from typing import Any

import httpx

from dialectica_ontology.compatibility.acled import acled_actor_to_dialectica, acled_to_dialectica
from dialectica_ontology.primitives import Actor, ConflictNode, Event
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

logger = logging.getLogger(__name__)

ACLED_API_URL = "https://api.acleddata.com/acled/read"
ACLED_KEY = os.getenv("ACLED_API_KEY", "")
ACLED_EMAIL = os.getenv("ACLED_EMAIL", "")


class ACLEDConnector:
    """Fetch and map ACLED events to ACO primitives."""

    def __init__(
        self,
        api_key: str | None = None,
        email: str | None = None,
    ) -> None:
        self._api_key = api_key or ACLED_KEY
        self._email = email or ACLED_EMAIL

    async def fetch_events(
        self,
        country: str | None = None,
        event_date_from: str | None = None,
        event_date_to: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch raw events from ACLED API."""
        params: dict[str, Any] = {
            "key": self._api_key,
            "email": self._email,
            "limit": limit,
        }
        if country:
            params["country"] = country
        if event_date_from:
            params["event_date"] = event_date_from
            params["event_date_where"] = ">="
        if event_date_to:
            params["event_date"] = event_date_to
            params["event_date_where"] = "<="

        async with httpx.AsyncClient() as client:
            resp = await client.get(ACLED_API_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])

    def map_to_primitives(
        self,
        events: list[dict[str, Any]],
        workspace_id: str = "",
        tenant_id: str = "",
    ) -> tuple[list[ConflictNode], list[ConflictRelationship]]:
        """Map ACLED events to ACO nodes and edges."""
        nodes: list[ConflictNode] = []
        edges: list[ConflictRelationship] = []
        actor_cache: dict[str, Actor] = {}

        for raw in events:
            # Map actors
            for actor_field in ["actor1", "actor2"]:
                actor_name = raw.get(actor_field, "")
                if actor_name and actor_name not in actor_cache:
                    actor_type = acled_actor_to_dialectica(raw.get(f"{actor_field}_type", ""))
                    actor = Actor(
                        name=actor_name,
                        actor_type=actor_type,
                        workspace_id=workspace_id,
                        tenant_id=tenant_id,
                        source_text=f"ACLED:{raw.get('data_id', '')}",
                    )
                    actor_cache[actor_name] = actor
                    nodes.append(actor)

            # Map event
            event_type = acled_to_dialectica(raw.get("event_type", ""))
            fatalities = int(raw.get("fatalities", 0))
            severity = min(1.0, fatalities / 100) if fatalities else 0.3

            occurred_at = None
            if raw.get("event_date"):
                with contextlib.suppress(ValueError, TypeError):
                    occurred_at = datetime.strptime(raw["event_date"], "%Y-%m-%d")

            event = Event(
                event_type=event_type,
                severity=severity,
                description=raw.get("notes", "")[:500],
                occurred_at=occurred_at,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                source_text=f"ACLED:{raw.get('data_id', '')}",
            )
            nodes.append(event)

            # Link actors to event
            for actor_field in ["actor1", "actor2"]:
                actor_name = raw.get(actor_field, "")
                if actor_name and actor_name in actor_cache:
                    edges.append(
                        ConflictRelationship(
                            type=EdgeType.PARTICIPATED_IN,
                            source_id=actor_cache[actor_name].id,
                            target_id=event.id,
                            source_label="Actor",
                            target_label="Event",
                            workspace_id=workspace_id,
                        )
                    )

        return nodes, edges
