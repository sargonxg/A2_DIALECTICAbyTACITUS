"""
GDELT Connector — Global Database of Events, Language, and Tone via BigQuery.

Queries gdelt-bq:gdeltv2.events filtering event_root_code for conflict events.
Maps Goldstein scale to ACO severity.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

from dialectica_ontology.primitives import Actor, Event, ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

logger = logging.getLogger(__name__)

# CAMEO event root codes for conflict-relevant events
CONFLICT_ROOT_CODES = ("14", "15", "16", "17", "18", "19", "20")


class GDELTConnector:
    """Fetch and map GDELT events from BigQuery to ACO primitives."""

    def __init__(self, project_id: str | None = None) -> None:
        self._project_id = project_id or os.getenv("GCP_PROJECT_ID", "")

    def _get_bq_client(self) -> Any:
        from google.cloud import bigquery
        return bigquery.Client(project=self._project_id)

    async def fetch_events(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        country_code: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query GDELT events from BigQuery."""
        conditions = [
            f"EventRootCode IN {CONFLICT_ROOT_CODES}",
        ]
        if date_from:
            conditions.append(f"SQLDATE >= '{date_from}'")
        if date_to:
            conditions.append(f"SQLDATE <= '{date_to}'")
        if country_code:
            conditions.append(
                f"(ActionGeo_CountryCode = '{country_code}' "
                f"OR Actor1CountryCode = '{country_code}')"
            )

        where = " AND ".join(conditions)
        query = f"""
            SELECT
                GLOBALEVENTID, SQLDATE, EventCode, EventRootCode,
                Actor1Name, Actor1CountryCode, Actor1Type1Code,
                Actor2Name, Actor2CountryCode, Actor2Type1Code,
                GoldsteinScale, NumMentions, AvgTone,
                ActionGeo_FullName, ActionGeo_Lat, ActionGeo_Long,
                SOURCEURL
            FROM `gdelt-bq.gdeltv2.events`
            WHERE {where}
            ORDER BY SQLDATE DESC
            LIMIT {limit}
        """

        try:
            client = self._get_bq_client()
            results = client.query(query)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("GDELT BigQuery query failed: %s", e)
            return []

    def map_to_primitives(
        self,
        events: list[dict[str, Any]],
        workspace_id: str = "",
        tenant_id: str = "",
    ) -> tuple[list[ConflictNode], list[ConflictRelationship]]:
        """Map GDELT events to ACO nodes and edges."""
        nodes: list[ConflictNode] = []
        edges: list[ConflictRelationship] = []
        actor_cache: dict[str, Actor] = {}

        for raw in events:
            for actor_field, type_field in [
                ("Actor1Name", "Actor1Type1Code"),
                ("Actor2Name", "Actor2Type1Code"),
            ]:
                name = raw.get(actor_field, "") or ""
                if name and name not in actor_cache:
                    actor_type = self._map_actor_type(raw.get(type_field, ""))
                    actor = Actor(
                        name=name,
                        actor_type=actor_type,
                        workspace_id=workspace_id,
                        tenant_id=tenant_id,
                        source_text=f"GDELT:{raw.get('GLOBALEVENTID', '')}",
                    )
                    actor_cache[name] = actor
                    nodes.append(actor)

            # Map Goldstein scale (-10 to +10) to severity (0 to 1)
            goldstein = float(raw.get("GoldsteinScale", 0) or 0)
            severity = max(0.0, min(1.0, (abs(goldstein) / 10.0)))

            occurred_at = None
            sqldate = str(raw.get("SQLDATE", ""))
            if len(sqldate) == 8:
                try:
                    occurred_at = datetime.strptime(sqldate, "%Y%m%d")
                except ValueError:
                    pass

            event = Event(
                event_type=self._map_event_code(raw.get("EventRootCode", "")),
                severity=severity,
                description=f"GDELT event {raw.get('GLOBALEVENTID', '')} at {raw.get('ActionGeo_FullName', '')}",
                occurred_at=occurred_at,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                source_text=f"GDELT:{raw.get('GLOBALEVENTID', '')}",
            )
            nodes.append(event)

            # Link actors
            for actor_field in ["Actor1Name", "Actor2Name"]:
                name = raw.get(actor_field, "") or ""
                if name and name in actor_cache:
                    edges.append(ConflictRelationship(
                        type=EdgeType.PARTICIPATED_IN,
                        source_id=actor_cache[name].id,
                        target_id=event.id,
                        source_label="Actor",
                        target_label="Event",
                        workspace_id=workspace_id,
                    ))

        return nodes, edges

    @staticmethod
    def _map_event_code(root_code: str) -> str:
        """Map CAMEO root code to ACO event type string."""
        mapping = {
            "14": "protest",
            "15": "exhibit_force_posture",
            "16": "reduce_relations",
            "17": "coerce",
            "18": "assault",
            "19": "assault",
            "20": "assault",
        }
        return mapping.get(str(root_code), "coerce")

    @staticmethod
    def _map_actor_type(type_code: str) -> str:
        """Map GDELT actor type code to ACO actor_type."""
        code = str(type_code).upper()
        if code in ("GOV", "MIL"):
            return "state"
        elif code in ("REB", "OPP", "INS"):
            return "armed_group"
        elif code in ("IGO",):
            return "organization"
        elif code in ("NGO", "MED"):
            return "organization"
        return "other"
