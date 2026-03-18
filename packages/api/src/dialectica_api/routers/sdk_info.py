"""
SDK Info Router — Discovery endpoint for cross-product integration.

Returns API metadata including ontology version, supported node/edge types,
theory frameworks, and endpoint paths. Used by Compass, PRAXIS, Wind Tunnel,
and ARGUS to dynamically discover DIALECTICA capabilities.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from dialectica_ontology.primitives import NODE_TYPES
from dialectica_ontology.relationships import EdgeType

router = APIRouter(prefix="/v1/sdk", tags=["sdk"])

# ── Theory framework registry (mirrors theory/__init__.py) ──────────────────

THEORY_FRAMEWORKS: list[str] = [
    "glasl",
    "fisher_ury",
    "kriesberg",
    "galtung",
    "lederach",
    "zartman",
    "deutsch",
    "thomas_kilmann",
    "french_raven",
    "mayer_trust",
    "plutchik",
    "pearl_causal",
    "winslade_monk",
    "ury_brett_goldberg",
    "burton",
]

# ── Endpoint catalogue ──────────────────────────────────────────────────────

ENDPOINT_CATALOGUE: dict[str, str] = {
    "extraction": "/v1/workspaces/{id}/extract",
    "entities": "/v1/workspaces/{id}/entities",
    "relationships": "/v1/workspaces/{id}/relationships",
    "graph": "/v1/workspaces/{id}/graph",
    "reasoning": "/v1/workspaces/{id}/reasoning/analyze",
    "theory_assess": "/v1/workspaces/{id}/theory/assess",
    "network_metrics": "/v1/workspaces/{id}/graph/network_metrics",
    "workspaces": "/v1/workspaces",
    "sdk_info": "/v1/sdk/info",
}


# ── Response model ──────────────────────────────────────────────────────────

class SDKInfoResponse(BaseModel):
    api_version: str
    ontology_version: str
    supported_tiers: list[str]
    node_types: list[str]
    edge_types: list[str]
    theory_frameworks: list[str]
    endpoints: dict[str, str]


# ── Endpoint ────────────────────────────────────────────────────────────────

@router.get("/info", response_model=SDKInfoResponse)
async def get_sdk_info() -> SDKInfoResponse:
    """Return DIALECTICA platform metadata for SDK clients.

    This endpoint is unauthenticated so that SDK bootstrapping and
    capability discovery can happen before auth is configured.
    """
    return SDKInfoResponse(
        api_version="1.0.0",
        ontology_version="2.0.1",
        supported_tiers=["essential", "standard", "full"],
        node_types=sorted(NODE_TYPES.keys()),
        edge_types=[e.value for e in EdgeType],
        theory_frameworks=THEORY_FRAMEWORKS,
        endpoints=ENDPOINT_CATALOGUE,
    )
