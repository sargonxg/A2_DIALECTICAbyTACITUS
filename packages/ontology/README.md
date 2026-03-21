# TACITUS Agentic Conflict Ontology (ACO) v2.0

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-orange.svg)](../../LICENSE)

The **Conflict Grammar** for computational conflict intelligence. 15 node types, 20 edge types, 25+ controlled vocabularies, 15 theory frameworks.

Part of [DIALECTICA by TACITUS](https://tacitus.me) — making conflict computable enough for better human judgment.

## Install

```bash
pip install dialectica-ontology
```

## Quick Start

```python
from dialectica_ontology import Actor, Conflict, Event, Interest
from dialectica_ontology.enums import ActorType, ConflictDomain

# Create typed conflict entities
actor = Actor(name="Party A", actor_type=ActorType.PERSON)
conflict = Conflict(
    name="Budget Dispute",
    domain=ConflictDomain.WORKPLACE,
    scale="micro",
    status="active",
    glasl_stage=3,
)

# Access tier-based ontology subsets
from dialectica_ontology.tiers import OntologyTier, get_available_nodes
essential_types = get_available_nodes(OntologyTier.ESSENTIAL)  # 7 types
full_types = get_available_nodes(OntologyTier.FULL)  # all 15 types
```

## 15 Node Types

| Node | Description | Tier |
|------|-------------|------|
| Actor | Entity with agency (person, org, state, coalition) | Essential |
| Conflict | Sustained friction pattern with Glasl stage | Essential |
| Event | Discrete occurrence (PLOVER 16-type coding) | Essential |
| Issue | Subject matter / incompatibility | Essential |
| Interest | Underlying need/fear (Fisher/Ury) | Standard |
| Norm | Rules, laws, contracts, policies | Standard |
| Process | ADR mechanisms (negotiation, mediation, arbitration) | Standard |
| Outcome | Results of processes | Standard |
| Narrative | Dominant/alternative/counter frames | Standard |
| PowerDynamic | French/Raven power bases | Standard |
| EmotionalState | Plutchik 8-primary emotions | Full |
| TrustState | Mayer/Davis/Schoorman model | Full |
| Location | Hierarchical geography | Full |
| Evidence | Supporting material with reliability scores | Full |
| Role | Contextual role reification | Full |

## 20 Edge Types

`PARTY_TO` · `PARTICIPATES_IN` · `HAS_INTEREST` · `PART_OF` · `CAUSED` · `AT_LOCATION` · `WITHIN` · `GOVERNED_BY` · `VIOLATES` · `RESOLVED_THROUGH` · `PRODUCES` · `ALLIED_WITH` · `OPPOSED_TO` · `HAS_POWER_OVER` · `MEMBER_OF` · `EXPERIENCES` · `TRUSTS` · `PROMOTES` · `ABOUT` · `EVIDENCED_BY`

## 15 Theory Frameworks

Burton, Deutsch, Fisher/Ury, French/Raven, Galtung, Glasl (9-stage), Kriesberg (7-phase), Lederach, Mayer/Davis/Schoorman (trust), Pearl (causal), Plutchik (emotions), Thomas-Kilmann, Ury/Brett/Goldberg, Winslade/Monk, Zartman (ripeness)

## Links

- [GitHub](https://github.com/sargonxg/A2_DIALECTICAbyTACITUS)
- [TACITUS](https://tacitus.me)

## License

Apache 2.0
