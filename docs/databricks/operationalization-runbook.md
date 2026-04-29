# Databricks operationalization runbook

This repo already has the core pieces for TACITUS/DIALECTICA:

- Neo4j as the live conflict graph.
- Gemini extraction and synthesis.
- GraphRAG and symbolic reasoning.
- KGE code for structural embeddings.
- A Databricks connector stub in `packages/reasoning/src/dialectica_reasoning/databricks_connector.py`.

The fastest Databricks path is to use it as the operational lakehouse around Neo4j: mirror graph snapshots into Delta, compute recurring graph health and actor-risk features, train structural models, and write compact operational signals back to Neo4j.

## Immediate setup

Create a Databricks secret scope named `tacitus` and store secrets with these keys:

```text
neo4j-uri
neo4j-user
neo4j-password
neo4j-database
gemini-api-key
```

Do not paste keys into notebooks. If credentials have already been shared in chat, rotate them first.

Import and run:

```text
notebooks/databricks/01_neo4j_delta_operational_signals.py
```

Set widgets:

```text
workspace_id = leave blank for all workspaces, or set one workspace id
secret_scope = tacitus
catalog = dialectica
schema = conflict_graphs
write_back_to_neo4j = false for first run, true after review
gemini_model = gemini-2.5-flash
```

The notebook creates:

```text
dialectica.conflict_graphs.nodes_bronze
dialectica.conflict_graphs.edges_bronze
dialectica.conflict_graphs.actor_features
dialectica.conflict_graphs.graph_quality_signals
```

## Concrete Databricks ideas

### 1. Neo4j to Delta graph mirror

Run the notebook on a schedule every 15 to 60 minutes. This gives you a queryable Delta history around the live graph without putting analytical load on Neo4j.

Near-term value:

- Count nodes and edges by ontology type.
- Detect low-confidence edges.
- Find important nodes without `EVIDENCED_BY` support.
- Produce workspace-level graph health metrics.

### 2. Operational graph dashboard

Use `actor_features` and `graph_quality_signals` as a Databricks SQL dashboard.

Useful tiles:

- Top actors by degree.
- Actors with many `OPPOSED_TO` edges.
- Conflicts with weak evidence coverage.
- Workspaces with sudden edge-count growth.
- Low-confidence relationship backlog for human review.

### 3. Human validation queue

Create a Delta table named `review_queue` from unsupported nodes and low-confidence edges.

Suggested columns:

```text
workspace_id, item_id, item_type, reason, severity, source_text, assigned_to, status, reviewed_at
```

Then use Neo4j write-back only for reviewed conclusions. This preserves the project principle: deterministic and human-validated facts should outrank probabilistic inference.

### 4. KGE training pipeline

Databricks is a good place to run PyKEEN because it can use larger clusters and GPU runtimes.

Flow:

```text
Neo4j edges -> Delta triples -> PyKEEN RotatE/TransE -> kge_predictions Delta table -> Neo4j inferred candidates
```

Do not automatically promote predicted relationships into the main graph. Store them as candidates with provenance:

```text
source = databricks_kge
confidence = model score
human_validated = false
```

### 5. GraphRAG evaluation harness

Use the seed benchmark data under `data/seed/benchmarks` as a Databricks evaluation set.

Track:

- answer groundedness,
- citation coverage,
- hallucination detector score,
- symbolic rule agreement,
- latency,
- token cost.

Write results to a Delta table and trend them over time before changing prompts, models, or graph schema.

### 6. Gemini batch extraction triage

Use Databricks to batch process raw documents and produce candidate extraction JSON before it enters DIALECTICA.

Best pattern:

```text
raw_docs Delta table -> Gemini extraction -> schema validation -> review_queue -> API/Neo4j ingest
```

That prevents a bad batch extraction from polluting the live graph.

### 7. TACITUS product signals

Turn graph metrics into product-facing signals:

- "watchlist actors" from degree plus opposition count.
- "evidence gaps" from unsupported key nodes.
- "escalation risk" from event velocity and Glasl-stage movement.
- "trust degradation" from recent `TRUSTS` and trust-breach patterns.
- "mediation readiness" from ripeness, power, and interest overlap.

These should become small, explicit `OperationalSignal` or `ReasoningTrace` nodes rather than freeform text blobs.

## Implementation warnings

The current `DatabricksConnector` is useful as a stub, but it should be hardened before production use:

- It builds SQL with string interpolation. Use parameterized statements or write through Spark DataFrames instead.
- `cluster_id` is passed as `warehouse_id` for SQL statement execution. Treat compute IDs and SQL warehouse IDs separately.
- The docs mention `databricks.py`, but the actual file is `databricks_connector.py`.
- The API docs mention an admin Databricks test endpoint, but the route may not exist yet. Verify before exposing it.

## Recommended next patch

Add a production-grade Databricks job with three tasks:

```text
01_neo4j_delta_operational_signals
02_train_kge_from_delta_triples
03_publish_review_queue
```

Then add API endpoints to fetch these signals:

```text
GET /v1/admin/graph-quality
GET /v1/workspaces/{id}/operational-signals
POST /v1/workspaces/{id}/signals/{signal_id}/validate
```
