# DIALECTICA Graph Pipeline Plan

Date: 2026-04-29

## 1. Current Stack Audit

DIALECTICA is already a multi-package Python/TypeScript system:

- `packages/ontology`: Pydantic v2 ontology models, relationships, symbolic
  rules, controlled vocabularies, theory modules, and subdomain detection.
- `packages/graph`: async graph interface plus Neo4j, Spanner, FalkorDB, Qdrant,
  traversal, vector, and writer modules.
- `packages/extraction`: LangGraph-style extraction pipeline with chunking,
  GLiNER prefilter, Gemini/Instructor extraction, validation, repair,
  relationship extraction, coreference, embeddings, and graph-write hooks.
- `packages/reasoning`: symbolic reasoning, graph quality, GraphRAG utilities,
  KGE, Databricks connector, and agents.
- `packages/api`: FastAPI app with extraction, graph, reasoning, benchmark,
  integration, health, auth, and admin routes.
- `apps/web`: Next.js 15 operator/frontend app, now including `/graphops`.
- `notebooks/databricks` and `infrastructure/databricks`: optional Databricks
  bundle jobs for book ingestion, AI extraction, Delta quality tables,
  Neo4j writeback, KGE candidates, and neurosymbolic benchmarks.

Current graph primitives are strong but v2-oriented: `Actor`, `Conflict`,
`Event`, `Issue`, `Interest`, `Norm`, `Process`, `Outcome`, `Narrative`,
`EmotionalState`, `TrustState`, `PowerDynamic`, `Location`, `Evidence`,
`Role`, `ReasoningTrace`, `InferredFact`, and `TheoryFrameworkNode`.

The current repo does not have a canonical YAML ontology artifact at
`ontology/tacitus_core_v1.yaml`, and it does not expose a packaged
`dialectica` CLI. Existing terminal tools live under `tools/` and use
`argparse`.

## 2. Current Gaps

- No explicit v1 YAML contract for the episode/provenance-first TACITUS core.
- Existing ontology has broad v2 primitives but lacks first-class v1 models for
  `Claim`, `Constraint`, `Leverage`, `Commitment`, `Episode`, `ActorState`,
  `SourceDocument`, `SourceChunk`, `EvidenceSpan`, and `ExtractionRun`.
- Existing sync extraction path records stats, while real graph persistence is
  in async graph write paths.
- `tools/ingest_text_to_neo4j.py` writes direct JSON to Neo4j and does not use
  canonical Pydantic models or `GraphClient`.
- No packaged CLI commands:
  - `dialectica ingest ./data/sample_docs`
  - `dialectica graph init`
  - `dialectica graph query "..."`
  - `dialectica graph episodes --case-id demo`
- Neo4j is implemented, but production GraphOps writeback requires fresh rotated
  Neo4j secrets in Vercel and Databricks.
- Databricks is useful but should remain optional; local mode needs a first-class
  JSONL/Parquet/DuckDB-or-SQLite path.

## 3. Proposed Target Architecture

The target is not generic RAG. The target is deterministic conflict memory:

```text
documents -> chunks -> source spans -> extraction run -> TACITUS primitives
-> ontology mapping -> temporal graph writes -> graph/vector retrieval
-> cited graph-grounded answer
```

Every graph object must carry:

- `workspace_id`
- `case_id`
- `episode_id` when episode-scoped
- `ontology_version`
- `source_id`
- `extraction_run_id`
- `confidence`
- `provenance_span`
- `valid_from`
- `valid_to`

Dynamic ontology extensions are allowed only if each custom type maps back to a
core primitive. Examples:

| Custom item | Core mapping |
| --- | --- |
| `RedLine` | `Constraint` or `Commitment` |
| `Ministry` | `Actor` |
| `Rumor` | `Narrative` or `Claim` |
| `Sanction` | `Constraint` or `Leverage` |
| `MediationTrack` | `Episode` or `Process` |

## 4. Neo4j-First Architecture

Neo4j is the operational graph memory.

Use the official Neo4j Python driver for primary graph writes and reads. The
current Neo4j Python driver docs recommend installing `neo4j`, creating a
driver with URI/auth, verifying connectivity, and parameterizing queries rather
than concatenating parameters.

GraphRAG for Python is useful but should be isolated behind adapters. Its KG
Builder is explicitly experimental, and the docs describe a pipeline of data
loader, text splitter, optional chunk embedder, schema builder, lexical graph
builder, entity/relation extractor, graph pruner, writer, and resolver. That
maps well to DIALECTICA, but DIALECTICA should keep its own ontology contract as
the source of truth.

Neo4j local mode:

- Docker Compose with `neo4j:5-community` or newer.
- APOC can be enabled in development with `NEO4J_PLUGINS=["apoc"]`; production
  should use least-privilege procedure allowlists.
- Constraints/indexes must cover ids and separation keys.

Required Neo4j env:

```text
NEO4J_URI
NEO4J_USERNAME or NEO4J_USER
NEO4J_PASSWORD
NEO4J_DATABASE
```

## 5. Databricks-Backed Architecture

Databricks is optional batch/lakehouse infrastructure, not required for MVP.

Use Declarative Automation Bundles for repeatable Databricks resources. Current
Databricks docs describe bundles as project-as-code configuration for validating,
deploying, and running workflows such as jobs and pipelines. Bundle resources
are declared under `resources` and include jobs, pipelines, schemas, secret
scopes, and more.

Recommended optional layout:

```text
databricks/
  databricks.yml
  resources/
    jobs.yml
  src/
    ingest_documents.py
    extract_to_delta.py
    sync_to_neo4j.py
    evaluate_extractions.py
```

Delta tables:

- `raw_documents`
- `source_chunks`
- `extraction_runs`
- `primitive_candidates`
- `ontology_mappings`
- `graph_ready_nodes`
- `graph_ready_edges`
- `benchmark_items`
- `benchmark_answers`
- `benchmark_judgments`

Mosaic AI Vector Search should index Delta chunk tables when Databricks is
configured. Databricks docs describe creating vector indexes from Delta tables,
syncing metadata, querying via API, and optionally computing embeddings from a
text column or using an existing array<float> embedding column.

Neo4j Spark connector is appropriate for large sync jobs. Its Databricks docs
cover reading from Neo4j, writing nodes, writing relationships, and writing with
Cypher queries.

## 6. In-House / Local Architecture Without Databricks

Local mode must remain productive:

- local files under `data/sample_docs` or user-provided directories,
- JSONL artifacts under `.dialectica/runs`,
- optional SQLite or DuckDB for indexed run metadata,
- local Parquet when `pyarrow` is available,
- local Neo4j Docker for graph memory,
- optional Qdrant/Faiss later for vector retrieval,
- Python CLI jobs for ingestion, mapping, graph writes, and query.

MVP local storage should be JSONL-first to avoid new heavy dependencies. DuckDB
or SQLite can be added once the primitive schema stabilizes.

## 7. Exact Incremental Implementation Plan

Critical vertical slice:

1. Add `ontology/tacitus_core_v1.yaml` as a human-readable ontology contract.
2. Add `dialectica/ontology/models.py` with strict Pydantic models:
   `Actor`, `Claim`, `Interest`, `Constraint`, `Leverage`, `Commitment`,
   `Event`, `Narrative`, `Episode`, `ActorState`, `SourceDocument`,
   `SourceChunk`, `EvidenceSpan`, `ExtractionRun`.
3. Add `dialectica/graph/base.py` with an adapter protocol.
4. Add `dialectica/graph/memory_adapter.py` for deterministic tests.
5. Add `dialectica/graph/neo4j_adapter.py` for scoped Neo4j writes and reads.
6. Add `dialectica/ingestion/` modules:
   - `load_documents.py`
   - `chunk_documents.py`
   - `extract_primitives.py`
   - `map_to_ontology.py`
   - `write_graph.py`
7. Add `dialectica/cli.py` using `argparse`, matching existing repo style.
8. Add root console script `dialectica = "dialectica.cli:main"`.
9. Add `data/sample_docs/` with a small open sample.
10. Add tests:
    - `tests/test_ontology_models.py`
    - `tests/test_temporal_actor_state.py`
    - `tests/test_graph_separation.py`
    - `tests/test_provenance_required.py`

Non-critical follow-up:

- Add Neo4j GraphRAG adapter behind `dialectica/graphrag/`.
- Add Text2Cypher adapter with allowlisted templates.
- Add local vector adapter.
- Add Databricks `/databricks` bundle mirror of the local pipeline.
- Add frontend upload/control path once CLI pipeline is stable.

## 8. Risks and Fallback Paths

- Risk: creating a parallel `dialectica` package may confuse the existing
  workspace packages. Fallback: keep it small as CLI/orchestration only and
  document that existing v2 packages remain intact.
- Risk: KG Builder API changes. Fallback: keep Neo4j GraphRAG use behind an
  adapter and do not depend on it for the MVP.
- Risk: Databricks secrets or spend. Fallback: local JSONL + Neo4j Docker mode.
- Risk: no LLM API key. Fallback: deterministic rule-based primitive extraction
  that produces clearly labeled `extraction_method="rule_based"` results.
- Risk: fake graph writes. Fallback: memory adapter for tests and explicit dry
  run output; Neo4j writes only when credentials are configured.

## 9. Required Env Vars / API Keys / User Setup

Minimum local graph:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=dialectica-dev
NEO4J_DATABASE=neo4j
```

Optional extraction:

```text
GEMINI_API_KEY=<rotated key>
OPENAI_API_KEY=<optional if OpenAI embeddings or GraphRAG adapter are used>
```

Optional Databricks:

```text
DATABRICKS_HOST
DATABRICKS_TOKEN
DATABRICKS_WAREHOUSE_ID
```

Security note: previously pasted secrets must be treated as exposed and rotated
before enabling production Neo4j writeback.

## 10. TODO List

Critical:

- [ ] Add `ontology/tacitus_core_v1.yaml`.
- [ ] Add v1 Pydantic models with required separation/provenance validators.
- [ ] Add graph adapter interface.
- [ ] Add memory adapter.
- [ ] Add Neo4j adapter with constraints and scoped writes.
- [ ] Add ingestion modules and sample documents.
- [ ] Add CLI commands for ingest, graph init, graph query, and episodes.
- [ ] Add tests for ontology, temporal state append-only behavior, graph
      separation, and provenance requirements.
- [ ] Update README with CLI quickstart.

Non-critical:

- [ ] Add Neo4j GraphRAG adapter.
- [ ] Add Databricks `/databricks` optional bundle.
- [ ] Add local vector search.
- [ ] Add frontend upload/control flow for the new CLI pipeline.
- [ ] Add benchmark report exporter with graph snapshot and prompt version.

## Sources Reviewed

- Neo4j GraphRAG for Python docs:
  https://neo4j.com/docs/neo4j-graphrag-python/current/
- Neo4j GraphRAG Knowledge Graph Builder:
  https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html
- Neo4j Python driver manual:
  https://neo4j.com/docs/python-manual/current/
- Neo4j APOC installation:
  https://neo4j.com/docs/apoc/current/installation/
- Neo4j Docker operations manual:
  https://neo4j.com/docs/operations-manual/current/docker/introduction/
- Neo4j Spark connector Databricks quickstart:
  https://neo4j.com/docs/spark/current/databricks/
- Databricks bundle commands:
  https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands
- Databricks bundle resources:
  https://docs.databricks.com/aws/en/dev-tools/bundles/resources
- Databricks Mosaic AI Vector Search:
  https://docs.databricks.com/aws/en/vector-search/vector-search
- Databricks vector index creation:
  https://docs.databricks.com/aws/en/vector-search/create-vector-search
