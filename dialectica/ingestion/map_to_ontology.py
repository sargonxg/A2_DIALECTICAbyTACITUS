"""Map extracted primitives to the TACITUS core ontology contract."""

from __future__ import annotations

from dialectica.ontology.models import GraphPrimitive
from dialectica.ontology.schema import core_primitive_names


def validate_core_mappings(primitives: list[GraphPrimitive]) -> list[str]:
    allowed = core_primitive_names()
    errors: list[str] = []
    for primitive in primitives:
        primitive_name = primitive.__class__.__name__
        if primitive_name not in allowed:
            errors.append(f"{primitive.id}: {primitive_name} is not in tacitus_core_v1")
    return errors
