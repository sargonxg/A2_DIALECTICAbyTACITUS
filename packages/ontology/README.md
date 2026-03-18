# TACITUS Agentic Conflict Ontology (ACO) v2.0

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-orange.svg)](../../LICENSE)

A graph-native ontology for modeling conflict, disputes, and negotiations across all scales — from interpersonal workplace disputes to geopolitical armed conflicts. Designed for neurosymbolic AI: deterministic Cypher/GQL queries + probabilistic GNN inference.

## Install

```bash
pip install dialectica-ontology
```

For development:

```bash
pip install -e packages/ontology
```

## Quick Start

```python
from dialectica_ontology import Actor, Conflict, Event
from dialectica_ontology.enums import (
    ActorType, ConflictScale, ConflictDomain, ConflictStatus, EventType
)
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from datetime import datetime

# Create actors
actor = Actor(
    name="UN Security Council",
    actor_type=ActorType.ORGANIZATION,
)

# Create a conflict
conflict = Conflict(
    name="Syria Civil War",
    scale=ConflictScale.MACRO,
    domain=ConflictDomain.ARMED,
    status=ConflictStatus.ACTIVE,
    glasl_stage=7,  # glasl_level auto-derived to LOSE_LOSE
)

# Create an event
event = Event(
    event_type=EventType.ASSAULT,
    severity=0.9,
    occurred_at=datetime(2023, 1, 15),
)

# Create a relationship
edge = ConflictRelationship(
    type=EdgeType.PARTY_TO,
    source_id=actor.id,
    target_id=conflict.id,
    source_label="Actor",
    target_label="Conflict",
    confidence=0.95,
)
```

## Features

### Ontology Structure

| Component | Count | Description |
|-----------|-------|-------------|
| **Node Types** | 15 | Actor, Conflict, Event, Issue, Interest, Norm, Process, Outcome, Narrative, EmotionalState, TrustState, PowerDynamic, Location, Evidence, Role |
| **Edge Types** | 20 | PARTY_TO, PARTICIPATES_IN, HAS_INTEREST, PART_OF, CAUSED, AT_LOCATION, WITHIN, ALLIED_WITH, OPPOSED_TO, HAS_POWER_OVER, MEMBER_OF, GOVERNED_BY, VIOLATES, RESOLVED_THROUGH, PRODUCES, EXPERIENCES, TRUSTS, PROMOTES, ABOUT, EVIDENCED_BY |
| **Enumerations** | 28 | Controlled vocabularies for every property (ActorType, GlaslStage, EventType, etc.) |
| **Theory Frameworks** | 16 | Glasl, Fisher/Ury, Kriesberg, Galtung, Lederach, Zartman, Deutsch, Thomas-Kilmann, French/Raven, Mayer Trust, Plutchik, Pearl Causal, Winslade/Monk, Ury/Brett/Goldberg, Burton |
| **Compatibility Mappers** | 4 | Bidirectional mappings for PLOVER, ACLED, UCDP, CAMEO |

### Three-Tier Progressive Disclosure

| Tier | Nodes | Edges | Use Case |
|------|-------|-------|----------|
| **Essential** | 7 | 6 | Quick conflict mapping |
| **Standard** | 12 | 13 | Structured analysis |
| **Full** | 15 | 20 | Complete neurosymbolic intelligence |

### Schema Generation

Generate database schemas from the canonical Pydantic models:

```python
from dialectica_ontology.schemas import (
    generate_cypher_ddl,    # Neo4j / FalkorDB
    generate_spanner_ddl,   # Google Cloud Spanner
    generate_gql_schema,    # Spanner Graph (GQL)
    generate_json_schema,   # API validation
    generate_turtle,        # OWL/RDF interoperability
)
```

### Validation

```python
from dialectica_ontology.validators import (
    validate_relationship_types,   # Edge schema compliance
    validate_subgraph,             # Full structural constraint checking
    validate_temporal_consistency,  # CAUSED edge temporal ordering
    validate_tier_compliance,       # Tier access control
)
```

## Documentation

Full documentation: [docs/ontology.md](../../docs/ontology.md)

## License

Apache 2.0
