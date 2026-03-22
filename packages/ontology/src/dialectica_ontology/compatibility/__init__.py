"""Compatibility mappings — PLOVER, CAMEO, ACLED, UCDP interoperability."""

from dialectica_ontology.compatibility.acled import (
    acled_actor_to_dialectica,
    acled_to_dialectica,
    dialectica_actor_to_acled,
    dialectica_to_acled,
)
from dialectica_ontology.compatibility.cameo import (
    cameo_event_to_dialectica,
    cameo_to_dialectica,
    dialectica_to_cameo,
    dialectica_to_cameo_event,
)
from dialectica_ontology.compatibility.plover import (
    dialectica_to_plover,
    event_type_quadclass,
    plover_quadclass,
    plover_to_dialectica,
)
from dialectica_ontology.compatibility.ucdp import (
    dialectica_to_ucdp_incompatibility,
    ucdp_conflict_type_label,
    ucdp_conflict_type_to_domain,
    ucdp_conflict_type_to_violence,
    ucdp_to_dialectica_incompatibility,
    ucdp_to_dialectica_intensity,
)

__all__ = [
    # PLOVER
    "plover_to_dialectica",
    "dialectica_to_plover",
    "plover_quadclass",
    "event_type_quadclass",
    # ACLED
    "acled_to_dialectica",
    "dialectica_to_acled",
    "acled_actor_to_dialectica",
    "dialectica_actor_to_acled",
    # CAMEO
    "cameo_to_dialectica",
    "dialectica_to_cameo",
    "cameo_event_to_dialectica",
    "dialectica_to_cameo_event",
    # UCDP
    "ucdp_to_dialectica_incompatibility",
    "dialectica_to_ucdp_incompatibility",
    "ucdp_to_dialectica_intensity",
    "ucdp_conflict_type_to_domain",
    "ucdp_conflict_type_to_violence",
    "ucdp_conflict_type_label",
]
