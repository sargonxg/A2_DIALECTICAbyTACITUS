# TACITUS Graph Architecture

DIALECTICA should be treated as the graph backbone for every TACITUS application.
The graph is not just storage. It is the operational memory, reasoning substrate,
review surface, and feedback loop.

## Core Principle

Every claim should be:

1. typed by the TACITUS ontology,
2. linked to source evidence,
3. scoped to a workspace and tenant,
4. assigned confidence,
5. reviewable by a human,
6. queryable by Neo4j,
7. analyzable by Databricks.

## What We Are Testing

The central claim is that a neurosymbolic architecture should outperform a
traditional LLM on conflict and human-friction reasoning because it separates:

- extraction from reasoning,
- evidence from inference,
- positions from interests,
- chronology from causality,
- narrative from fact,
- policy constraints from preferences.

A normal LLM can produce a plausible answer directly from text. DIALECTICA should
produce an answer through an inspectable chain:

```text
source text -> ontology candidates -> Neo4j situation graph -> symbolic checks
-> Databricks graph quality -> graph-grounded answer -> benchmark score
```

## Why Databricks + Neo4j

Neo4j and Databricks play different roles.

Neo4j is the live graph memory. It answers connected questions:

- who is party to the conflict,
- who has power over whom,
- what caused escalation,
- what evidence supports a claim,
- which norms govern the situation,
- which narratives each actor promotes.

Databricks is the analytical and experimental layer. It handles:

- repeatable ingestion jobs,
- Delta tables for every intermediate artifact,
- batch AI extraction through `ai_query`,
- quality metrics and review queues,
- benchmark runs,
- future graph embeddings and link prediction.

Together, they create a loop:

```text
Neo4j -> Delta snapshot -> Databricks quality/AI/benchmark -> OperationalSignal -> Neo4j
```

## Current Live Proof

The first Databricks demo job has run successfully:

- Job: `[dev giulio] tacitus-dialectica-book-ai-extraction-demo`
- Run: `227559218086552`
- Source: Project Gutenberg Romeo and Juliet
- Output tables:
  - `dialectica.conflict_graphs.raw_text_chunks` with 35 rows
  - `dialectica.conflict_graphs.ai_extraction_candidates` with 35 rows

This proves the workspace can ingest open text and create ontology candidate
rows with Databricks AI Functions. The next step is writing those candidates into
Neo4j after the Databricks secret scope contains Neo4j connection secrets.

## Graph Layers

| Layer | Question | Example nodes | Example edges |
| --- | --- | --- | --- |
| Source graph | Where did this come from? | `Document`, `Chunk`, `Evidence` | `CONTAINS`, `NEXT_CHUNK`, `EVIDENCED_BY` |
| Situation graph | What is happening? | `Actor`, `Conflict`, `Event`, `Issue`, `Interest`, `Norm` | `PARTY_TO`, `CAUSED`, `HAS_INTEREST`, `VIOLATES` |
| Theory graph | Why is this analytically meaningful? | `TheoryFrameworkNode`, `OntologyType` | `EXPLAINS`, `USES_FEATURE`, `MAPS_TO` |
| Reasoning graph | What did TACITUS infer? | `ReasoningTrace`, `InferredFact`, `OperationalSignal` | `DERIVED_FROM`, `CONTRADICTS`, `SUPPORTS` |
| Activity graph | What did users do? | `User`, `Project`, `Workspace`, `ReviewDecision` | `REVIEWED`, `APPROVED`, `REJECTED`, `CORRECTED` |
| Signal graph | What did Databricks compute? | `GraphMetric`, `LinkCandidate`, `ReviewQueueItem` | `FLAGS`, `SUGGESTS`, `SCORES` |

## Book-Based Ingestion Process

Start with open public-domain books because they are dense, legal, repeatable
test data:

| Book | Gutenberg ID | Best TACITUS test |
| --- | --- | --- |
| Romeo and Juliet | 1513 | Family conflict, escalation, emotions, mediation failure |
| War and Peace | 2600 | Macro conflict, alliances, command hierarchy, causal chains |
| Crime and Punishment | 2554 | Norm violation, confession, guilt, trust, narratives |
| The Federalist Papers | 1404 | Political conflict, institutional design, public argument |

Terminal loop:

```powershell
uv run python tools/download_gutenberg.py 1513 --output data/raw/romeo_juliet.txt --max-chars 80000
uv run python tools/apply_neo4j_schema.py
uv run python tools/ingest_text_to_neo4j.py data/raw/romeo_juliet.txt --workspace-id books-romeo-juliet --tenant-id tacitus-lab
databricks bundle run tacitus_operational_loop -t dev --profile tacitus
```

## Gemini Role

Gemini should be used for structured extraction, not free-form conclusions.
The extractor should ask for JSON only, using the 15 allowed node labels and 20
allowed edge types. Any field outside the contract should be rejected or placed
in metadata for review.

Use Gemini for:

- entity and relation extraction,
- evidence quote selection,
- claim normalization,
- uncertainty explanation,
- analyst review summaries.

Do not use Gemini to override deterministic symbolic conclusions. If a symbolic
rule detects a violation or graph inconsistency, LLM output can explain it but
should not erase it.

## Databricks Role

Databricks should run the operational analytics layer:

- snapshot Neo4j into Delta,
- compute graph quality,
- identify missing evidence,
- rank low-confidence edges,
- compute centrality and actor features,
- generate link prediction candidates,
- write `OperationalSignal` nodes back to Neo4j.

Default job policy: manual runs only until data model and costs are stable.

## First Product Surface

The protected page at `/graphops` should be used as the TACITUS operating console:

- shows the pipeline,
- explains graph layers,
- visualizes a situation graph,
- lists ontology nodes and relationships,
- provides allowlisted Neo4j query tests,
- links analysts from raw text to graph structure to Databricks signals.

Set these environment variables in the web deployment:

```text
GRAPHOPS_BASIC_USER=tacitus
GRAPHOPS_BASIC_PASSWORD=<strong generated password>
NEO4J_URI=<neo4j+s uri>
NEO4J_USERNAME=<user>
NEO4J_PASSWORD=<password>
NEO4J_DATABASE=neo4j
```

Suggested password shape: four random words plus digits and symbols, stored only
in the deployment environment or a password manager.
