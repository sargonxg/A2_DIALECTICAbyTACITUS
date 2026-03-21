"""
UCDP Connector — Uppsala Conflict Data Program.

REST client for https://ucdpapi.pcr.uu.se/api/.
Maps UCDP dyads to ACO Actor pairs with Conflict nodes.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

import httpx

from dialectica_ontology.primitives import Actor, Conflict, Event, ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from dialectica_ontology.compatibility.ucdp import (
    ucdp_to_dialectica_incompatibility,
    ucdp_to_dialectica_intensity,
    ucdp_conflict_type_to_domain,
)

logger = logging.getLogger(__name__)

UCDP_API_URL = "https://ucdpapi.pcr.uu.se/api"


class UCDPConnector:
    """Fetch and map UCDP conflict data to ACO primitives."""

    async def fetch_conflicts(
        self,
        year: int | None = None,
        region: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch armed conflicts from UCDP API."""
        params: dict[str, Any] = {"pagesize": limit, "page": 0}
        if year:
            params["year"] = year

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{UCDP_API_URL}/ucdpprioconflict/{year or ''}",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("Result", [])

    async def fetch_events(
        self,
        country_id: int | None = None,
        year: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch UCDP Georeferenced Event Dataset entries."""
        params: dict[str, Any] = {"pagesize": limit, "page": 0}
        if country_id:
            params["Country"] = country_id
        if year:
            params["year"] = year

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{UCDP_API_URL}/gedevents/{year or ''}",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("Result", [])

    def map_conflicts_to_primitives(
        self,
        conflicts: list[dict[str, Any]],
        workspace_id: str = "",
        tenant_id: str = "",
    ) -> tuple[list[ConflictNode], list[ConflictRelationship]]:
        """Map UCDP conflicts to ACO Conflict + Actor nodes."""
        nodes: list[ConflictNode] = []
        edges: list[ConflictRelationship] = []
        actor_cache: dict[str, Actor] = {}

        for raw in conflicts:
            # Create Conflict node
            incompatibility = ucdp_to_dialectica_incompatibility(
                raw.get("Incompatibility", "")
            )
            intensity = ucdp_to_dialectica_intensity(
                raw.get("IntensityLevel", 0)
            )
            domain = ucdp_conflict_type_to_domain(
                raw.get("TypeOfConflict", "")
            )

            conflict = Conflict(
                name=raw.get("ConflictName", raw.get("Location", "Unknown")),
                scale="macro",
                domain=domain,
                status="active" if raw.get("ActiveYear", 0) else "latent",
                description=f"UCDP Conflict ID {raw.get('ConflictId', '')}",
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                source_text=f"UCDP:{raw.get('ConflictId', '')}",
            )
            nodes.append(conflict)

            # Create Actor nodes for sides
            for side_field in ["SideA", "SideB"]:
                side_name = raw.get(side_field, "")
                if side_name and side_name not in actor_cache:
                    actor = Actor(
                        name=side_name,
                        actor_type="state" if side_field == "SideA" else "armed_group",
                        workspace_id=workspace_id,
                        tenant_id=tenant_id,
                        source_text=f"UCDP:{raw.get('ConflictId', '')}",
                    )
                    actor_cache[side_name] = actor
                    nodes.append(actor)

                if side_name and side_name in actor_cache:
                    edges.append(ConflictRelationship(
                        type=EdgeType.PARTY_TO,
                        source_id=actor_cache[side_name].id,
                        target_id=conflict.id,
                        source_label="Actor",
                        target_label="Conflict",
                        workspace_id=workspace_id,
                    ))

            # Opposition edge between sides
            side_a = raw.get("SideA", "")
            side_b = raw.get("SideB", "")
            if side_a in actor_cache and side_b in actor_cache:
                edges.append(ConflictRelationship(
                    type=EdgeType.OPPOSED_TO,
                    source_id=actor_cache[side_a].id,
                    target_id=actor_cache[side_b].id,
                    source_label="Actor",
                    target_label="Actor",
                    workspace_id=workspace_id,
                ))

        return nodes, edges
