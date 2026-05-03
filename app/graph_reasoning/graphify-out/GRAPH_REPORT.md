# Graph Report - app\graph_reasoning  (2026-05-03)

## Corpus Check
- 10 files · ~5,671 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 139 nodes · 296 edges · 7 communities detected
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]

## God Nodes (most connected - your core abstractions)
1. `CozoReasoningClient` - 30 edges
2. `Neo4jGraphReasoningClient` - 22 edges
3. `GraphReasoningService` - 22 edges
4. `GraphReasoningObject` - 20 edges
5. `ObjectKind` - 19 edges
6. `GraphReasoningEdge` - 18 edges
7. `GraphitiTemporalClient` - 15 edges
8. `ReasoningQueries` - 15 edges
9. `GraphReasoningSqlStore` - 15 edges
10. `DialecticaIngestionAdapter` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Pre-ingestion pipeline utilities for large text and dynamic ontology.` --uses--> `ObjectKind`  [INFERRED]
  pipeline.py → schema.py
- `CozoReasoningClient` --uses--> `GraphReasoningEdge`  [INFERRED]
  cozo_client.py → schema.py
- `CozoReasoningClient` --uses--> `GraphReasoningObject`  [INFERRED]
  cozo_client.py → schema.py
- `CozoReasoningClient` --uses--> `ObjectKind`  [INFERRED]
  cozo_client.py → schema.py
- `ReasoningQueries` --uses--> `CozoReasoningClient`  [INFERRED]
  reasoning_queries.py → cozo_client.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (15): BaseModel, Graph reasoning subsystem., GraphReasoningHealth, HealthCheck, IngestResult, IngestTextRequest, GraphReasoningSqlStore, _model_dict() (+7 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (18): AdaptedGraph, DialecticaIngestionAdapter, Dialectica text ingestion adapter for graph reasoning., Normalize text into provenance-bearing reasoning objects., Neo4j source-of-truth client for graph reasoning objects., Thin async Neo4j adapter using separate subsystem labels., EdgeKind, GraphReasoningEdge (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (5): CozoReasoningClient, CozoDB reasoning mirror., Return raw rows from an embedded Cozo relation when available., Read-optimized reasoning mirror with Cozo-compatible relation names., _relation_for_kind()

### Community 3 - "Community 3"
Cohesion: 0.24
Nodes (2): _json_safe(), Neo4jGraphReasoningClient

### Community 4 - "Community 4"
Cohesion: 0.19
Nodes (5): _filter_related(), _other_id(), Reasoning queries over the Cozo-style mirror., Datalog-style query facade over relation-shaped mirror data., ReasoningQueries

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (10): build_dynamic_ontology(), build_pipeline_plan(), _chunk(), chunk_text(), clean_source_text(), PipelinePlan, _profile_mappings(), Pre-ingestion pipeline utilities for large text and dynamic ontology. (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (3): GraphitiTemporalClient, Graphiti temporal/provenance adapter., Temporal layer on Neo4j with optional native Graphiti integration.

## Knowledge Gaps
- **3 isolated node(s):** `Schema for the optional graph reasoning subsystem.`, `A provenance-carrying reasoning object mirrored across graph layers.`, `A typed edge that never exists without provenance.`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 3`** (16 nodes): `_json_safe()`, `Neo4jGraphReasoningClient`, `.changed_since()`, `.close()`, `.fetch_recent()`, `.find_source_by_hash()`, `.get_actor()`, `._get_driver()`, `.health()`, `.__init__()`, `.initialize_schema()`, `.search()`, `._session()`, `.upsert_edges()`, `.upsert_objects()`, `neo4j_client.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CozoReasoningClient` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`?**
  _High betweenness centrality (0.287) - this node is a cross-community bridge._
- **Why does `GraphReasoningService` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `Neo4jGraphReasoningClient` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `CozoReasoningClient` (e.g. with `GraphReasoningEdge` and `GraphReasoningObject`) actually correct?**
  _`CozoReasoningClient` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Neo4jGraphReasoningClient` (e.g. with `GraphReasoningEdge` and `GraphReasoningObject`) actually correct?**
  _`Neo4jGraphReasoningClient` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `GraphReasoningService` (e.g. with `CozoReasoningClient` and `GraphitiTemporalClient`) actually correct?**
  _`GraphReasoningService` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `GraphReasoningObject` (e.g. with `CozoReasoningClient` and `CozoDB reasoning mirror.`) actually correct?**
  _`GraphReasoningObject` has 16 INFERRED edges - model-reasoned connections that need verification._