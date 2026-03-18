"""
TACITUS Core Ontology — Re-export from canonical package.

The original 1,020-line ontology definition has been archived to
docs/legacy/ontology_v1_reference.py. This module re-exports the
canonical Pydantic v2 implementation from packages/ontology/.

Usage unchanged:
    from ontology import Actor, Conflict, Event, EdgeType
"""

from dialectica_ontology.primitives import *  # noqa: F401, F403
from dialectica_ontology.relationships import *  # noqa: F401, F403
from dialectica_ontology.enums import *  # noqa: F401, F403
from dialectica_ontology.schemas import generate_cypher_ddl, generate_spanner_ddl  # noqa: F401
