# Dynamic Ontology Operating Model

DIALECTICA should not be one rigid ontology. It should be a stable core plus
dynamic profiles that adapt to a user, situation, source base, and objective.

The stable core answers: what is the situation, who is involved, what happened,
what evidence supports it, what is inferred, and what still needs review.

Dynamic profiles answer: what does this specific expert need to see?

## Research Anchors

- W3C PROV-O is the right mental model for provenance: claims, sources, agents,
  derivations, primary sources, and generated artifacts.
- W3C OWL-Time is the right mental model for temporal graph structure: instants,
  intervals, ordering, durations, and temporal reference systems.
- Neo4j property graphs are the right operational store for live situation
  queries because relationships are first-class and fast to traverse.
- Databricks is the right analytical engine for repeatable extraction,
  quality scoring, benchmark runs, and Delta tables of every intermediate state.

## Core Graph Layers

| Layer | Purpose | Key labels |
| --- | --- | --- |
| Identity | user/project/workspace separation | `User`, `Project`, `Workspace`, `Situation` |
| Source | provenance and trust | `Source`, `Document`, `Chunk`, `Evidence`, `Claim` |
| Situation | conflict substance | `Actor`, `Conflict`, `Event`, `Issue`, `Interest`, `Norm`, `Process`, `Outcome` |
| Temporal | event and phase reasoning | `Episode`, `TemporalInstant`, `TemporalInterval`, `ConflictPhase` |
| Reasoning | inferred and reviewable facts | `Inference`, `ReasoningTrace`, `OperationalSignal`, `ReviewDecision` |
| Profile | dynamic ontology behavior | `OntologyProfile`, `ProfileRequirement`, `QuestionType`, `UseCase` |

## Claim Lifecycle

Every LLM-extracted fact must become a claim with state:

```text
candidate -> extracted -> graph_validated -> human_verified -> superseded/rejected
```

Recommended properties:

```text
claim_status: candidate | extracted | graph_validated | human_verified | rejected | superseded
assertion_type: explicit | inferred | user_asserted | model_hypothesis | imported
source_trust: trusted | user_direct | institutional | public_domain | uncertain | sketchy
confidence: 0.0-1.0
review_required: true/false
```

The key rule: an LLM may propose inferred facts, but it does not silently promote
them into verified facts.

## Temporal Ontology for Conflict

Conflict experts do not only ask “what happened?” They ask where a situation is
in time:

- latent tension,
- triggering episode,
- escalation,
- polarization,
- stalemate,
- negotiation window,
- settlement,
- implementation,
- relapse,
- transformation.

Represent this with:

```text
(:Situation)-[:HAS_EPISODE]->(:Episode)
(:Episode)-[:HAS_PHASE]->(:ConflictPhase)
(:Event)-[:OCCURS_DURING]->(:TemporalInterval)
(:Event)-[:PRECEDES]->(:Event)
(:Event)-[:CAUSED]->(:Event)
(:Event)-[:ESCALATES]->(:Conflict)
(:Event)-[:DE_ESCALATES]->(:Conflict)
```

Keep temporal order separate from causality. `PRECEDES` is not `CAUSED`.

## Dynamic Ontology Profiles

### Human Friction Profile

Best for workplace, family, mediation, teams, and interpersonal conflict.

Adds emphasis on:

- commitments,
- trust,
- emotional state,
- role expectations,
- narrative drift,
- apology/repair opportunities,
- contested scope,
- face-saving constraints.

### Literary Conflict Profile

Best for books and narrative analysis.

Adds emphasis on:

- characters as actors,
- scenes as episodes,
- narrative frames,
- internal conflict,
- alliances,
- turning points,
- tragic inevitability,
- explicit quote provenance.

### Political/Policy Profile

Best for governance, public policy, institutional disputes, and diplomacy.

Adds emphasis on:

- institutions,
- jurisdictions,
- legal norms,
- procedural constraints,
- veto players,
- coalitions,
- public narratives,
- implementation risks.

### Mediation/Resolution Profile

Best for practitioners trying to intervene.

Adds emphasis on:

- interests versus positions,
- BATNA hints,
- ZOPA candidates,
- trust repair,
- ripeness,
- process options,
- mediator leverage,
- immediate next questions.

## Databricks Responsibilities

Databricks should maintain the repeatable operating loop:

1. ingest source material into `raw_text_chunks`,
2. extract ontology candidates into `ai_extraction_candidates`,
3. parse candidates into node/edge candidates,
4. score source and claim reliability,
5. produce review queues,
6. write accepted graph facts to Neo4j,
7. snapshot Neo4j into Delta,
8. benchmark baseline LLM versus graph-grounded TACITUS.

Current Delta tables introduced for dynamic ontology operations:

| Table | Purpose |
| --- | --- |
| `ontology_profile_coverage` | Measures whether a workspace has enough labels for human-friction, literary, policy, or mediation profiles. |
| `source_reliability_signals` | Tracks source trust class, candidate volume, chunk count, and extraction freshness. |
| `temporal_event_signals` | Measures temporal node and edge density for event/process/outcome reasoning. |
| `claim_review_queue` | Converts low-confidence or weak-evidence claims into reviewable work. |

## Neo4j Responsibilities

Neo4j should answer live connected questions:

- Which actors are party to this situation?
- Which source supports this claim?
- Which events caused escalation?
- Which claims are inferred but unverified?
- Which norms govern this episode?
- Which interests are hidden behind positions?
- Which phase is the conflict in?
- What changed after the latest event?

Recommended Neo4j indexes and constraints are in:

```text
infrastructure/neo4j/dynamic_graph_layers.cypher
```

This adds first-class graph support for:

- `Workspace`,
- `Project`,
- `Situation`,
- `Episode`,
- `Claim`,
- `Source`,
- `Chunk`,
- `OntologyProfile`,
- `TemporalInterval`,
- `ConflictPhase`.

## Publication-Grade Claim

DIALECTICA is useful if it can show that:

```text
ordinary LLM answer < graph-grounded answer < graph-grounded + reviewed answer
```

The benchmark should measure:

- provenance F1,
- graph overlap,
- causal precision,
- contradiction detection,
- temporal ordering,
- source reliability handling,
- expert usefulness.

This is the core publication argument: structured neurosymbolic conflict
intelligence improves the reliability and usefulness of LLM reasoning about
human friction.
