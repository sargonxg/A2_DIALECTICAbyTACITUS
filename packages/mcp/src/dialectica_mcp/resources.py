"""
MCP Resources — Expose workspace list and ontology schema as MCP resources.
"""
from __future__ import annotations

import json
from typing import Any


def get_ontology_schema() -> dict[str, Any]:
    """Return the DIALECTICA ontology schema as a dict."""
    from dialectica_ontology import NODE_TYPES, EDGE_SCHEMA
    from dialectica_ontology.tiers import TIER_CONFIGS

    node_types = [
        {
            "name": type(n).__name__,
            "fields": list(n.model_fields.keys()) if hasattr(n, "model_fields") else [],
        }
        for n in NODE_TYPES
    ]

    edge_types = [
        {
            "type": edge_type,
            "source_label": schema.get("source_label", ""),
            "target_label": schema.get("target_label", ""),
        }
        for edge_type, schema in EDGE_SCHEMA.items()
    ]

    tiers = {
        tier.value: {
            "description": config.get("description", ""),
            "node_count": config.get("node_count", 0),
            "edge_count": config.get("edge_count", 0),
        }
        for tier, config in TIER_CONFIGS.items()
    }

    return {
        "name": "DIALECTICA Conflict Grammar Ontology v2.0",
        "node_types": node_types,
        "edge_types": edge_types,
        "tiers": tiers,
    }


def register_resources(mcp: Any) -> None:
    """Register MCP resources on the server."""

    @mcp.resource("dialectica://ontology/schema")
    def ontology_schema() -> str:
        """The DIALECTICA Conflict Grammar ontology schema."""
        return json.dumps(get_ontology_schema(), indent=2, default=str)

    @mcp.resource("dialectica://ontology/node-types")
    def node_types() -> str:
        """List of all 15 DIALECTICA node types."""
        from dialectica_ontology import NODE_TYPES
        types = [type(n).__name__ for n in NODE_TYPES]
        return json.dumps(types)

    @mcp.resource("dialectica://ontology/tiers")
    def tier_info() -> str:
        """Ontology tier configurations (essential, standard, full)."""
        from dialectica_ontology.tiers import TIER_CONFIGS
        return json.dumps(
            {t.value: c for t, c in TIER_CONFIGS.items()},
            indent=2,
            default=str,
        )
