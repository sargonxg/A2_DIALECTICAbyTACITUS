# Tier System — DIALECTICA Ontology

Comprehensive reference for the three-tier access model that controls progressive
disclosure of ontology complexity in the DIALECTICA conflict analysis system.

**Source module:** `packages/ontology/src/dialectica_ontology/tiers.py`

---

## 1. Overview

The DIALECTICA ontology contains 15 node types, 20 edge types, and a rich set of
analytical features. Exposing the full ontology in every context creates unnecessary
complexity for simple use cases and increases computational cost for downstream
consumers (LLM prompts, graph queries, API payloads).

The tier system solves this by organizing the ontology into three cumulative levels
of progressive complexity:

| Tier | Nodes | Edges | Features | Purpose |
|---|---|---|---|---|
| **Essential** | 7 | 6 | 6 | Quick conflict mapping |
| **Standard** | 12 | 13 | 13 | Structured analysis |
| **Full** | 15 | 20 | 22 | Complete neurosymbolic intelligence |

Each tier is **cumulative** -- Standard includes everything in Essential, and Full
includes everything in Standard. This means upgrading a tier never removes access to
previously available types; it only adds new ones.

### Why tiers exist

- **Reduced cognitive load.** A journalist mapping a conflict does not need
  Plutchik emotion wheels or French-Raven power bases. The Essential tier gives
  them exactly what they need: actors, events, locations, and outcomes.
- **Smaller LLM context windows.** Sending 15 node schemas into a prompt when
  only 7 are needed wastes tokens and can degrade extraction quality.
- **Faster queries.** Graph traversals over a smaller type set run faster and
  return cleaner results.
- **Graduated onboarding.** New users start with Essential and unlock more
  complexity as their analysis demands it.

---

## 2. Tier Definitions

### Essential Tier

> **"Core conflict mapping -- actors, events, locations, and resolution processes"**

The Essential tier provides the minimum viable ontology for mapping any conflict.
It answers the fundamental questions: who is involved, what happened, where did it
happen, and how is it being resolved.

- **7 node types** -- Actor, Conflict, Event, Issue, Process, Outcome, Location
- **6 edge types** -- PARTY_TO, PARTICIPATES_IN, PART_OF, AT_LOCATION, RESOLVED_THROUGH, PRODUCES
- **6 feature flags** -- conflict_mapping, event_timeline, actor_identification, spatial_mapping, process_tracking, outcome_recording

### Standard Tier

> **"Structured analysis -- adds interests, norms, narratives, evidence, and roles"**

The Standard tier adds analytical depth. It enables interest-based analysis (Fisher/Ury),
norm compliance checking, narrative mapping, evidence linking, and role assignment.
It also unlocks Glasl escalation staging and Kriesberg lifecycle analysis.

- **12 node types** -- Essential + Interest, Norm, Narrative, Evidence, Role
- **13 edge types** -- Essential + HAS_INTEREST, GOVERNED_BY, VIOLATES, ABOUT, EVIDENCED_BY, WITHIN, MEMBER_OF
- **13 feature flags** -- Essential + interest_analysis, norm_compliance, narrative_analysis, evidence_linking, role_assignment, glasl_escalation, kriesberg_lifecycle

### Full Tier

> **"Complete neurosymbolic intelligence -- emotions, trust, power dynamics, causal reasoning"**

The Full tier unlocks the complete ontology, including affective state tracking
(Plutchik emotions), trust modeling (Mayer/Davis/Schoorman), power dynamics
(French & Raven), alliance/opposition detection, and causal reasoning (Pearl hierarchy).

- **15 node types** -- Standard + EmotionalState, TrustState, PowerDynamic
- **20 edge types** -- Standard + EXPERIENCES, TRUSTS, PROMOTES, HAS_POWER_OVER, ALLIED_WITH, OPPOSED_TO, CAUSED
- **22 feature flags** -- Standard + emotion_tracking, trust_assessment, power_analysis, alliance_detection, causal_reasoning, neurosymbolic_inference, plutchik_wheel, french_raven_power, mayer_trust_model

---

## 3. Node Types by Tier

The following table shows every node type and the tier at which it becomes available.

| # | Node Type | Tier | Group | Theoretical Basis |
|---|---|---|---|---|
| 1 | **Actor** | Essential | Core | CAMEO/ACLED actor coding + Fisher/Ury |
| 2 | **Conflict** | Essential | Core | UCDP + Galtung ABC + Glasl + Kriesberg |
| 3 | **Event** | Essential | Core | PLOVER event-mode-context + ACLED |
| 4 | **Issue** | Essential | Structure | UCDP incompatibility + Fisher/Ury |
| 5 | **Process** | Essential | Process | Ury/Brett/Goldberg + ADR taxonomy + Glasl |
| 6 | **Outcome** | Essential | Process | Mnookin "Beyond Winning" + ADR |
| 7 | **Location** | Essential | Context | ACLED/UCDP spatial coding |
| 8 | **Interest** | Standard | Structure | Fisher/Ury "Getting to Yes" + Rothman |
| 9 | **Norm** | Standard | Structure | LKIF + CLO + Fisher/Ury "objective criteria" |
| 10 | **Narrative** | Standard | Context | Winslade & Monk + Sara Cobb + Dewulf |
| 11 | **Evidence** | Standard | Context | Legal evidence law + ACLED source methodology |
| 12 | **Role** | Standard | Context | SEM (Simple Event Model) role reification |
| 13 | **EmotionalState** | Full | State | Plutchik wheel + Smith & Ellsworth appraisal |
| 14 | **TrustState** | Full | State | Mayer/Davis/Schoorman integrative model |
| 15 | **PowerDynamic** | Full | State | French & Raven + Ury/Brett/Goldberg |

### Nodes added at each tier

**Essential (7):**

| Node | Description |
|---|---|
| Actor | Any entity capable of agency in a conflict |
| Conflict | A sustained pattern of friction between parties |
| Event | A discrete, time-bounded occurrence that alters conflict state |
| Issue | The subject matter or incompatibility at stake |
| Process | Any procedure or mechanism for addressing conflict |
| Outcome | The result of a resolution process or conflict itself |
| Location | Geographic entity, hierarchically structured |

**Standard adds (5):**

| Node | Description |
|---|---|
| Interest | An underlying need, desire, concern, or fear -- the WHY behind a position |
| Norm | Any rule, standard, or shared expectation governing behavior |
| Narrative | A dominant story or frame shaping conflict understanding |
| Evidence | Supporting material for claims, events, or assertions |
| Role | A contextual role played by an actor in a specific conflict or event |

**Full adds (3):**

| Node | Description |
|---|---|
| EmotionalState | An actor's emotional condition at a point in time |
| TrustState | Trust level between two actors (ability, benevolence, integrity) |
| PowerDynamic | A measured power relationship between actors |

---

## 4. Edge Types by Tier

The following table shows every edge type and the tier at which it becomes available.

| # | Edge Type | Source | Target | Tier |
|---|---|---|---|---|
| 1 | **PARTY_TO** | Actor | Conflict | Essential |
| 2 | **PARTICIPATES_IN** | Actor | Event | Essential |
| 3 | **PART_OF** | Event | Conflict | Essential |
| 4 | **AT_LOCATION** | Event | Location | Essential |
| 5 | **RESOLVED_THROUGH** | Conflict | Process | Essential |
| 6 | **PRODUCES** | Process | Outcome | Essential |
| 7 | **HAS_INTEREST** | Actor | Interest | Standard |
| 8 | **GOVERNED_BY** | Conflict | Norm | Standard |
| 9 | **VIOLATES** | Event | Norm | Standard |
| 10 | **ABOUT** | Narrative | Conflict | Standard |
| 11 | **EVIDENCED_BY** | Event | Evidence | Standard |
| 12 | **WITHIN** | Location | Location | Standard |
| 13 | **MEMBER_OF** | Actor | Actor | Standard |
| 14 | **EXPERIENCES** | Actor | EmotionalState | Full |
| 15 | **TRUSTS** | Actor | Actor | Full |
| 16 | **PROMOTES** | Actor | Narrative | Full |
| 17 | **HAS_POWER_OVER** | Actor | Actor | Full |
| 18 | **ALLIED_WITH** | Actor | Actor | Full |
| 19 | **OPPOSED_TO** | Actor | Actor | Full |
| 20 | **CAUSED** | Event | Event | Full |

### Edges added at each tier

**Essential (6):** Core structural relationships -- linking actors to conflicts,
events to conflicts and locations, conflicts to resolution processes, and processes
to outcomes.

**Standard adds (7):** Analytical relationships -- linking actors to interests,
conflicts to governing norms, events to violated norms and supporting evidence,
narratives to conflicts, locations to parent locations, and actors to groups.

**Full adds (7):** State and causal relationships -- linking actors to emotional
states, trust assessments, power dynamics, alliances, and oppositions. Also adds
causal links between events and narrative promotion by actors.

---

## 5. Feature Flags by Tier

Feature flags indicate which analytical capabilities are available at each tier.
Use `get_available_features(tier)` to retrieve the set for a given tier.

### Essential Features (6)

| Feature Flag | Description |
|---|---|
| `conflict_mapping` | Core conflict identification and structuring |
| `event_timeline` | Temporal event sequencing |
| `actor_identification` | Actor extraction and classification |
| `spatial_mapping` | Geographic location mapping |
| `process_tracking` | Resolution process monitoring |
| `outcome_recording` | Outcome documentation |

### Standard Features (adds 7, total 13)

| Feature Flag | Description |
|---|---|
| `interest_analysis` | Fisher/Ury interest identification and BATNA assessment |
| `norm_compliance` | Norm applicability and violation detection |
| `narrative_analysis` | Narrative mapping and frame analysis |
| `evidence_linking` | Evidence association and reliability scoring |
| `role_assignment` | Actor role classification in context |
| `glasl_escalation` | Glasl 9-stage escalation model assessment |
| `kriesberg_lifecycle` | Kriesberg 7-phase conflict lifecycle tracking |

### Full Features (adds 9, total 22)

| Feature Flag | Description |
|---|---|
| `emotion_tracking` | Actor emotional state monitoring |
| `trust_assessment` | Mayer/Davis/Schoorman trust decomposition |
| `power_analysis` | French & Raven power base identification |
| `alliance_detection` | Actor alliance and opposition mapping |
| `causal_reasoning` | Pearl causal hierarchy analysis |
| `neurosymbolic_inference` | Combined symbolic + neural inference |
| `plutchik_wheel` | Plutchik 8-primary emotion classification with dyads |
| `french_raven_power` | 6-base power type decomposition and asymmetry measurement |
| `mayer_trust_model` | Ability/benevolence/integrity trust scoring |

---

## 6. Use Cases

### When to use Essential

- **Rapid conflict mapping.** You need a quick overview of who is involved, what
  happened, and where.
- **Journalism and reporting.** Producing a conflict timeline with key actors and
  events.
- **First-pass triage.** Scanning a large corpus to identify and catalog conflicts
  before deeper analysis.
- **Lightweight integrations.** Systems that only need basic conflict graph data
  (dashboards, alert systems).
- **LLM extraction with limited context.** When prompt space is constrained, sending
  only 7 node schemas yields better extraction quality.

### When to use Standard

- **Structured conflict analysis.** Understanding not just what happened but why --
  interests, norms, and narratives.
- **Mediation preparation.** Identifying party interests, BATNA positions, governing
  norms, and competing narratives before a mediation session.
- **Legal and compliance analysis.** Tracking norm violations, evidence chains, and
  actor roles (claimant, respondent, witness).
- **Escalation monitoring.** Using Glasl staging and Kriesberg lifecycle phases to
  track conflict trajectory.
- **Research with evidence requirements.** Academic or policy analysis that needs
  source attribution and evidence reliability scoring.

### When to use Full

- **Deep neurosymbolic analysis.** Full-spectrum conflict intelligence combining
  symbolic reasoning with continuous features.
- **Academic conflict research.** Applying the complete set of 15 theory frameworks
  to a conflict.
- **Trust and power dynamics.** Modeling the trust relationships and power asymmetries
  that drive conflict behavior.
- **Emotional trajectory analysis.** Tracking how actor emotions evolve over the
  conflict lifecycle using Plutchik classification.
- **Causal modeling.** Building causal chains between events with temporal validation
  (cause must precede effect).
- **Alliance network analysis.** Mapping formal and informal alliances and
  oppositions between actors.
- **Early warning systems.** Using the full feature set for predictive conflict
  modeling.

---

## 7. Tier Validation

The `validate_tier_compliance()` function in `validators.py` checks that a graph
conforms to the constraints of a specified tier.

### How it works

```python
from dialectica_ontology.validators import validate_tier_compliance
from dialectica_ontology.tiers import OntologyTier

errors = validate_tier_compliance(nodes, relationships, OntologyTier.STANDARD)
if errors:
    for e in errors:
        print(f"Violation: {e}")
else:
    print("Graph is compliant with the Standard tier.")
```

### Validation logic

1. **Retrieve allowed types.** The function calls `get_available_nodes(tier)` and
   `get_available_edges(tier)` to get the set of permitted node labels and edge
   type names for the requested tier.

2. **Check every node.** For each `ConflictNode` in the input, its `label` field
   is checked against the allowed node set. If the label is not in the set, an
   error is recorded:
   ```
   Node 'abc123' has label 'EmotionalState' not available in standard tier
   ```

3. **Check every edge.** For each `ConflictRelationship` in the input, its `type`
   field (resolved to a string) is checked against the allowed edge set. If the
   type is not in the set, an error is recorded:
   ```
   Edge 'def456' has type 'CAUSED' not available in standard tier
   ```

4. **Return errors.** The function returns `list[str]`. An empty list means the
   graph is fully compliant with the specified tier. Each string is a human-readable
   error message identifying the specific node or edge that violates the tier.

### Combining with other validators

Tier validation is typically used alongside the other validators in `validators.py`:

```python
from dialectica_ontology.validators import (
    validate_subgraph,
    validate_temporal_consistency,
    validate_tier_compliance,
)
from dialectica_ontology.tiers import OntologyTier

# Structural validation (source/target existence + edge schema)
errors = validate_subgraph(nodes, relationships)

# Temporal validation (CAUSED edges: cause precedes effect)
errors += validate_temporal_consistency(relationships, node_timestamps)

# Tier compliance (all types within selected tier)
errors += validate_tier_compliance(nodes, relationships, OntologyTier.STANDARD)

if errors:
    raise ValueError(f"Graph validation failed:\n" + "\n".join(errors))
```

---

## 8. API Usage

### Specifying a tier

The tier is specified using the `OntologyTier` enum, which is a `StrEnum` with
three values:

```python
from dialectica_ontology.tiers import OntologyTier

tier = OntologyTier.ESSENTIAL   # "essential"
tier = OntologyTier.STANDARD    # "standard"
tier = OntologyTier.FULL        # "full"
```

In API requests, the tier is passed as a lowercase string: `"essential"`,
`"standard"`, or `"full"`.

### Querying available types

Use the helper functions to discover what is available at a given tier:

```python
from dialectica_ontology.tiers import (
    OntologyTier,
    get_available_nodes,
    get_available_edges,
    get_available_features,
)

tier = OntologyTier.STANDARD

nodes = get_available_nodes(tier)
# {'Actor', 'Conflict', 'Event', 'Issue', 'Process', 'Outcome',
#  'Location', 'Interest', 'Norm', 'Narrative', 'Evidence', 'Role'}

edges = get_available_edges(tier)
# {'PARTY_TO', 'PARTICIPATES_IN', 'PART_OF', 'AT_LOCATION',
#  'RESOLVED_THROUGH', 'PRODUCES', 'HAS_INTEREST', 'GOVERNED_BY',
#  'VIOLATES', 'ABOUT', 'EVIDENCED_BY', 'WITHIN', 'MEMBER_OF'}

features = get_available_features(tier)
# {'conflict_mapping', 'event_timeline', 'actor_identification',
#  'spatial_mapping', 'process_tracking', 'outcome_recording',
#  'interest_analysis', 'norm_compliance', 'narrative_analysis',
#  'evidence_linking', 'role_assignment', 'glasl_escalation',
#  'kriesberg_lifecycle'}
```

### Accessing tier configuration

The `TIER_CONFIGS` dictionary provides a summary for each tier including counts
and the full sets:

```python
from dialectica_ontology.tiers import TIER_CONFIGS, OntologyTier

config = TIER_CONFIGS[OntologyTier.ESSENTIAL]
print(config["name"])           # "Essential"
print(config["description"])    # "Core conflict mapping -- ..."
print(config["node_count"])     # 7
print(config["edge_count"])     # 6
print(config["feature_count"])  # 6
print(config["nodes"])          # frozenset({'Actor', 'Conflict', ...})
print(config["edges"])          # frozenset({'PARTY_TO', ...})
print(config["features"])       # frozenset({'conflict_mapping', ...})
```

### Feature flag checking

To check whether a specific analytical capability is available at a tier:

```python
from dialectica_ontology.tiers import OntologyTier, get_available_features

def is_feature_available(feature: str, tier: OntologyTier) -> bool:
    return feature in get_available_features(tier)

is_feature_available("glasl_escalation", OntologyTier.ESSENTIAL)   # False
is_feature_available("glasl_escalation", OntologyTier.STANDARD)    # True
is_feature_available("glasl_escalation", OntologyTier.FULL)        # True
```

---

## 9. Upgrading Between Tiers

### Upgrade path

Tiers form a strict hierarchy:

```
Essential  -->  Standard  -->  Full
 (7/6/6)       (12/13/13)     (15/20/22)
```

Upgrading is always additive. Moving from Essential to Standard adds 5 node types,
7 edge types, and 7 feature flags. Moving from Standard to Full adds 3 node types,
7 edge types, and 9 feature flags.

### What changes when upgrading

| Aspect | Essential -> Standard | Standard -> Full |
|---|---|---|
| **New node types** | Interest, Norm, Narrative, Evidence, Role | EmotionalState, TrustState, PowerDynamic |
| **New edge types** | HAS_INTEREST, GOVERNED_BY, VIOLATES, ABOUT, EVIDENCED_BY, WITHIN, MEMBER_OF | EXPERIENCES, TRUSTS, PROMOTES, HAS_POWER_OVER, ALLIED_WITH, OPPOSED_TO, CAUSED |
| **New features** | interest_analysis, norm_compliance, narrative_analysis, evidence_linking, role_assignment, glasl_escalation, kriesberg_lifecycle | emotion_tracking, trust_assessment, power_analysis, alliance_detection, causal_reasoning, neurosymbolic_inference, plutchik_wheel, french_raven_power, mayer_trust_model |
| **Theory frameworks unlocked** | Glasl Escalation, Kriesberg Lifecycle, Fisher-Ury Principled Negotiation, Winslade-Monk Narrative Mediation | Plutchik Emotions, French-Raven Power, Mayer Trust Model, Pearl Causal Hierarchy |

### Backward compatibility

A graph built at a higher tier can always be validated against a lower tier by
checking tier compliance. If the graph only uses types from the lower tier, it
passes validation even though it was created in a higher-tier context.

Conversely, a graph built at a lower tier is automatically valid at any higher
tier, since higher tiers are strict supersets.

### Migration pattern

To upgrade a graph's tier, no data migration is needed. Simply change the tier
parameter in API requests and begin using the newly available types:

```python
from dialectica_ontology.tiers import OntologyTier

# Previously using Essential -- now upgrade to Standard
tier = OntologyTier.STANDARD

# New node types are now available for creation
# Existing Essential nodes and edges remain valid
# Validation will now accept Standard-tier types
```

To downgrade, verify compliance first:

```python
from dialectica_ontology.validators import validate_tier_compliance
from dialectica_ontology.tiers import OntologyTier

# Check if current graph can fit in Essential tier
errors = validate_tier_compliance(nodes, relationships, OntologyTier.ESSENTIAL)
if errors:
    print(f"Cannot downgrade: {len(errors)} types exceed Essential tier")
    for e in errors:
        print(f"  - {e}")
else:
    print("Safe to downgrade to Essential tier")
```

---

## Data Model Reference

For the complete node and edge type specifications (fields, types, enumerations),
see the [Ontology Reference](ontology.md).

For theory framework details, see the [Theory Frameworks Reference](theory-frameworks.md).
