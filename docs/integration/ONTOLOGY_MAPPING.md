# Ontology Mapping

How AGON primitives and KAIROS outputs translate into DIALECTICA's Conflict Grammar (15 node types, 20 edge types, 25+ vocabularies).

> Reference: DIALECTICA ontology at `packages/ontology/src/dialectica_ontology/primitives.py` + `relationships.py`. Conflict Grammar v2.0.

---

## Why this matters

KAIROS and AGON emit their own primitives. Without explicit mapping rules, DIALECTICA's fusion layer makes inconsistent choices, graphs drift, queries return wrong things. This document is the authoritative translation table.

---

## KAIROS → Conflict Grammar

### Actors

| KAIROS field | Conflict Grammar | Notes |
|---|---|---|
| `actor.canonical_name` | `Actor.name` | Direct |
| `actor.aliases[]` | `Actor.aliases[]` | Direct |
| KAIROS actor type (inferred) | `Actor.actor_type` | Map: `person`→PERSON, `organization`→ORG, `state`→STATE |
| `actor.spans[]` | `Actor.evidence_spans[]` | Preserve all spans |
| KAIROS local ID | `Actor.merged_from_kairos` | Foreign key, kept for traceability |

**Merge rule:** if AGON emits same canonical_name + type, merge into single canonical Actor; keep both local IDs as merge sources.

### Events

| KAIROS `Event` | Conflict Grammar `Event` | Notes |
|---|---|---|
| `event.canonical_label` | `Event.description` | Direct |
| `event.timestamp.iso8601` | `Event.occurred_at` | Preserve resolution |
| `event.fuzziness` | `Event.temporal_confidence` | EXACT→1.0, APPROX→0.7, RELATIVE→0.4, UNRESOLVED→0.0 |
| `event.participants[]` | edges: `(Actor)-[:PARTICIPATES_IN]->(Event)` | One edge per participant |
| `event.plover_type` | `Event.plover_type` | DIALECTICA's existing 16-type taxonomy |
| `event.severity` | `Event.severity` | 1-10 |
| `event.spans[]` | `Event.evidence_spans[]` | Preserve |

### AllenRelations

| KAIROS `AllenRelation` | Conflict Grammar | Notes |
|---|---|---|
| `BEFORE` | edge `(Event)-[:PRECEDES]->(Event)` | New edge type, additive |
| `AFTER` | reversed `PRECEDES` | Don't double-store |
| `MEETS` | edge `(Event)-[:MEETS]->(Event)` | New |
| `OVERLAPS` / `OVERLAPPED_BY` | edge `(Event)-[:OVERLAPS]->(Event) { direction }` | Single edge with direction prop |
| `DURING` / `CONTAINS` | edge `(Event)-[:DURING]->(Episode)` | Episode container relationship |
| `STARTS` / `STARTED_BY` | edge `(Event)-[:STARTS]->(Episode) { reversed: bool }` | |
| `FINISHES` / `FINISHED_BY` | edge `(Event)-[:FINISHES]->(Episode) { reversed: bool }` | |
| `EQUALS` | edge `(Event)-[:COTEMPORAL]->(Event)` | New |

**Action item:** Conflict Grammar v2.1 adds these temporal edges. Track in DIALECTICA ontology migration.

### Episodes

KAIROS Episode → DIALECTICA `Phase` node (existing in Conflict Grammar under Conflict.phases).

| KAIROS `Episode` | Conflict Grammar `Phase` |
|---|---|
| `episode.boundaries.start` | `Phase.started_at` |
| `episode.boundaries.end` | `Phase.ended_at` |
| `episode.anchors[]` | edge `(Phase)-[:ANCHORED_BY]->(Event)` |
| `episode.confidence` | `Phase.confidence` |
| `episode.review_state` | `Phase.review_status` |

### Commitments

KAIROS `Commitment` → DIALECTICA `Commitment` node (new in Conflict Grammar v2.1, currently in `Norm` as workaround).

| KAIROS field | Conflict Grammar |
|---|---|
| `commitment.committer` | edge `(Actor)-[:COMMITTED]->(Commitment)` |
| `commitment.target` | edge `(Commitment)-[:TO]->(Actor)` |
| `commitment.content` | `Commitment.content` |
| `commitment.state` | `Commitment.state` (enum: pledged/active/fulfilled/breached/contested/withdrawn) |
| `commitment.deadline` | `Commitment.deadline` |
| Breach inferred | edge `(Actor)-[:VIOLATES]->(Commitment)` |

**Action item:** Add `Commitment` to Conflict Grammar v2.1 as first-class node. Until then, store as `Norm` with `norm_type="commitment"`.

### Friction

KAIROS `FrictionObject` → multiple Conflict Grammar edges.

| KAIROS friction kind | Conflict Grammar |
|---|---|
| `conflict` direct | edge `(Actor)-[:OPPOSED_TO]->(Actor)` |
| `cooperation` | edge `(Actor)-[:ALLIED_WITH]->(Actor)` |
| `ambiguity` | no edge; stored as `Hypothesis` node |
| `trajectory: escalating` | property on edge: `trajectory="escalating"` |
| `mechanism` | property on edge: `friction_mechanism="..."` |
| `evidence_grade` | property on edge: `evidence_grade="..."` |

### Hypotheses

KAIROS `Hypothesis` → DIALECTICA `Narrative` node (existing) with `narrative_type="hypothesis"`.

---

## AGON → Conflict Grammar

### Actors

Same mapping as KAIROS. Use `Actor.merged_from_agon` for trace. Reconcile with KAIROS-emitted actors at fusion time.

### Claims

AGON `Claim` → DIALECTICA `Assertion` node (new, Conflict Grammar v2.1) OR `Event` if claim represents an action.

| AGON field | Conflict Grammar |
|---|---|
| `claim.subject` | edge `(Actor)-[:ASSERTS]->(Assertion)` |
| `claim.predicate` | `Assertion.predicate` |
| `claim.object` (Actor) | edge `(Assertion)-[:ABOUT]->(Actor)` |
| `claim.object` (Event) | edge `(Assertion)-[:ABOUT]->(Event)` |
| `claim.object` (string) | `Assertion.object_text` |
| `claim.evidence[]` | edges `(Assertion)-[:EVIDENCED_BY]->(Evidence)` |
| `claim.verification` | `Assertion.verification_status` (verified/unresolved/contradicted/denied) |
| `claim.confidence` | `Assertion.confidence` |

**Action item:** Add `Assertion` to Conflict Grammar v2.1. Until then, model as `Narrative` with `narrative_type="assertion"`.

### Contradictions

AGON `Contradiction` → DIALECTICA edge.

| AGON field | Conflict Grammar |
|---|---|
| `contradiction.claim_a` + `claim_b` | edge `(Assertion)-[:CONTRADICTS]->(Assertion)` |
| `contradiction.mechanism` | edge property |
| `contradiction.severity` | edge property |
| `contradiction.explanation` | edge property `rationale` |

**Action item:** Add `CONTRADICTS` to Conflict Grammar v2.1 edge taxonomy.

### Denials

AGON denial (`Claim.verification = DENIED`) → DIALECTICA composite:
- `Assertion` with `verification_status = denied`
- edge `(Actor)-[:DENIES]->(Assertion)` from the denier
- If denial contradicts another claim: also `CONTRADICTS` edge.

**Action item:** Add `DENIES` to Conflict Grammar v2.1.

### Commitments (AGON variant)

If AGON also extracts commitments (when KAIROS not in pipeline), map identically to KAIROS commitments. AGON commitment IDs become foreign keys on the Commitment node.

**Conflict resolution:** if both AGON and KAIROS emit commitments for the same span, prefer KAIROS (temporal precision). Log AGON's version as alternative in `Commitment.alternative_extractions`.

### Friction matrix

AGON's actor-by-actor friction matrix → series of `(Actor)-[:OPPOSED_TO|ALLIED_WITH|FRICTION_WITH]->(Actor)` edges.

### Quality gates

AGON quality gates → graph-level metadata, not nodes/edges:
- `Workspace.quality_gates = { evidence_coverage: 0.78, ambiguity_score: 0.12, ... }`
- Surfaced in UI as warnings/health indicators.

### Inference findings

AGON deterministic findings (denied obligations, contested commitments, escalation loops) → DIALECTICA reasoning layer outputs:
- Stored as `ReasoningResult` records (existing).
- Cited in agent responses.
- Not stored as graph nodes (these are derived, not primary).

---

## Conflict Grammar v2.1 additions (driven by integration)

To support AGON + KAIROS cleanly, DIALECTICA's ontology needs additive changes. Tracked as Conflict Grammar v2.1.

### New node types

| Node | From | Why |
|---|---|---|
| `Assertion` | AGON `Claim` | Distinguish claims-about-the-world from `Norm`/`Event` |
| `Commitment` | KAIROS `Commitment` | First-class instead of `Norm` workaround |
| `Episode` (alias `Phase`) | KAIROS `Episode` | Aligns vocabulary |
| `Hypothesis` (alias `Narrative` subtype) | KAIROS `Hypothesis` | Mark as inferential |

### New edge types

| Edge | Direction | Purpose |
|---|---|---|
| `CONTRADICTS` | Assertion ↔ Assertion | AGON contradictions |
| `DENIES` | Actor → Assertion | AGON denials |
| `PRECEDES` | Event → Event | Allen BEFORE |
| `MEETS` | Event → Event | Allen MEETS |
| `OVERLAPS` | Event → Event (with direction prop) | Allen OVERLAPS/OVERLAPPED_BY |
| `DURING` | Event → Episode | Allen DURING/CONTAINS |
| `STARTS` | Event → Episode | Allen STARTS |
| `FINISHES` | Event → Episode | Allen FINISHES |
| `COTEMPORAL` | Event → Event | Allen EQUALS |
| `ANCHORED_BY` | Episode → Event | Episode boundaries |
| `COMMITTED` | Actor → Commitment | Replaces `PARTY_TO` for commitments |
| `TO` | Commitment → Actor | Recipient of commitment |
| `ASSERTS` | Actor → Assertion | Who's making the claim |

### New enums

- `VerificationStatus`: verified / unresolved / contradicted / denied
- `CommitmentState`: pledged / active / fulfilled / breached / contested / withdrawn
- `ContradictionMechanism`: direct_negation / date_inconsistency / attribution_dispute / obligation_denial / semantic

---

## Fusion algorithm (DIALECTICA-side pseudocode)

```python
def fuse(kairos_output: KairosOutput, agon_output: AgonOutput) -> ConflictGraph:
    graph = ConflictGraph()

    # 1. Canonicalize actors
    actor_map = canonicalize_actors(
        kairos_output.actors,
        agon_output.actors,
        workspace_registry=graph.actor_registry,
    )

    # 2. Import KAIROS events with timestamps + Allen relations
    for ev in kairos_output.events:
        node = graph.add_event(
            id=ev.id,
            description=ev.canonical_label,
            occurred_at=ev.timestamp,
            participants=[actor_map[a] for a in ev.participants],
            spans=ev.spans,
        )
    for rel in kairos_output.relations:
        graph.add_temporal_edge(rel)

    # 3. Import KAIROS commitments
    for c in kairos_output.commitments:
        graph.add_commitment(c, actor_map)

    # 4. Import AGON claims as Assertions
    for claim in agon_output.claims:
        graph.add_assertion(
            id=claim.id,
            subject=actor_map[claim.subject],
            predicate=claim.predicate,
            object=resolve_object(claim.object, actor_map, graph.events),
            evidence=claim.evidence,
            verification=claim.verification,
        )

    # 5. Add contradictions as edges
    for contra in agon_output.contradictions:
        graph.add_edge(
            "CONTRADICTS",
            contra.claim_a, contra.claim_b,
            mechanism=contra.mechanism,
            severity=contra.severity,
        )

    # 6. Friction edges
    for f in kairos_output.frictions + agon_output.friction_matrix:
        graph.add_friction_edge(f, actor_map)

    # 7. Quality metadata at workspace level
    graph.workspace.quality_gates = agon_output.quality_gates

    return graph
```

---

## Open mapping questions

1. **Overlap between AGON Claim and DIALECTICA Event.** AGON claim "Sam said X" is metadata about a speech act; DIALECTICA Event might already cover speech events. Recommendation: AGON Claims always map to `Assertion`, never to `Event`. Events come from KAIROS or extraction pipeline.

2. **Trust signals.** AGON emits weak `TrustState`-like signals via friction matrix. DIALECTICA has full Mayer/Davis/Schoorman `TrustState` node. Don't auto-map; surface AGON friction as edges, leave TrustState population to DIALECTICA reasoning.

3. **Power dynamics.** Same as trust. AGON friction is the trigger; DIALECTICA's reasoning layer computes PowerDynamic nodes from accumulated evidence.

4. **Multi-document coreference.** KAIROS today is single-document. When KAIROS adds corpus-level merging, who owns actor canonicalization across documents — KAIROS or DIALECTICA workspace registry? Recommendation: DIALECTICA workspace registry remains authoritative; KAIROS emits per-document candidates.

---

*See [`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md) for the code wiring.*
