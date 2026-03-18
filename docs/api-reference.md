# DIALECTICA API Reference

Complete endpoint reference for the DIALECTICA REST API. The API is built with
FastAPI and serves conflict graph data, theory assessments, symbolic reasoning,
extraction pipelines, and administrative operations.

**Base URL (local dev):** `http://localhost:8080`

---

## Authentication

All endpoints except `/health` require a tenant identity header. Admin
endpoints additionally require the `X-Admin-Key` header.

| Header | Required by | Description |
|---|---|---|
| `X-Tenant-ID` | All `/v1/*` endpoints | Tenant identifier; set to `admin` for superuser access |
| `X-Admin-Key` | Admin endpoints | Secret key stored in GCP Secret Manager (`ADMIN_API_KEY`) |

---

## Health

Tag: **health** — Router file: `packages/api/src/dialectica_api/routers/health.py`

### GET /health

Basic liveness check. No authentication required.

**Response model:** `HealthResponse`

| Field | Type | Description |
|---|---|---|
| `status` | string | Always `"ok"` |
| `timestamp` | string | UTC ISO-8601 timestamp |
| `version` | string | API version (default `"1.0.0"`) |

```bash
curl http://localhost:8080/health
```

### GET /health/dependencies

Check connectivity to backing services (graph database).

**Response model:** `DependencyHealth`

| Field | Type | Description |
|---|---|---|
| `graph_backend` | string | Configured backend (`spanner`, `neo4j`, etc.) |
| `graph_connected` | boolean | Whether the graph client responded |
| `graph_status` | string | `"connected"`, `"disconnected"`, or error message |

```bash
curl http://localhost:8080/health/dependencies \
  -H "X-Tenant-ID: admin"
```

---

## Workspaces

Tag: **workspaces** — Prefix: `/v1/workspaces`

Router file: `packages/api/src/dialectica_api/routers/workspaces.py`

### POST /v1/workspaces

Create a new conflict workspace.

**Request body:** `WorkspaceCreate`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | *(required)* | Human-readable workspace name |
| `domain` | string | `"political"` | Conflict domain |
| `scale` | string | `"macro"` | Analysis scale |
| `tier` | string | `"standard"` | Ontology tier: `essential`, `standard`, `full` |
| `description` | string | `""` | Free-text description |

**Response (201):** `WorkspaceResponse`

```bash
curl -X POST http://localhost:8080/v1/workspaces \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"name": "Syria Civil War", "domain": "political", "tier": "full"}'
```

### GET /v1/workspaces

List all workspaces for the current tenant.

**Response:** `list[WorkspaceResponse]`

```bash
curl http://localhost:8080/v1/workspaces -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}

Get a workspace by ID. Returns node/edge counts when graph client is available.

**Response:** `WorkspaceResponse`

| Field | Type | Description |
|---|---|---|
| `id` | string | Workspace identifier |
| `name` | string | Human-readable name |
| `domain` | string | Conflict domain |
| `scale` | string | Analysis scale |
| `tier` | string | Ontology tier |
| `description` | string | Description |
| `tenant_id` | string | Owning tenant |
| `created_at` | string | ISO-8601 creation timestamp |
| `node_count` | int | Total graph nodes |
| `edge_count` | int | Total graph edges |

```bash
curl http://localhost:8080/v1/workspaces/abc12345 -H "X-Tenant-ID: demo"
```

### PATCH /v1/workspaces/{workspace_id}

Update workspace metadata (name, domain, scale, description).

**Request body:** `WorkspaceUpdate` — all fields optional.

```bash
curl -X PATCH http://localhost:8080/v1/workspaces/abc12345 \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"description": "Updated description"}'
```

### DELETE /v1/workspaces/{workspace_id}

Delete a workspace. Returns `204 No Content`.

```bash
curl -X DELETE http://localhost:8080/v1/workspaces/abc12345 \
  -H "X-Tenant-ID: demo"
```

---

## Entities

Tag: **entities** — Prefix: `/v1/workspaces/{workspace_id}/entities`

Router file: `packages/api/src/dialectica_api/routers/entities.py`

### GET /v1/workspaces/{workspace_id}/entities

List entities (graph nodes) with optional label filter.

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `label` | string | `null` | Filter by node label (e.g. `Actor`, `Event`) |
| `limit` | int | `50` | Max results (max 500) |
| `offset` | int | `0` | Pagination offset |

**Response:** `list[NodeResponse]`

| Field | Type | Description |
|---|---|---|
| `id` | string | Node identifier |
| `label` | string | Ontology node type |
| `name` | string | Human-readable name |
| `properties` | object | All non-core properties |
| `confidence` | float | Extraction confidence (0.0-1.0) |

```bash
curl "http://localhost:8080/v1/workspaces/abc12345/entities?label=Actor&limit=20" \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/entities/{entity_id}

Get a single entity by ID. Returns `404` if not found.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/entities/actor-001 \
  -H "X-Tenant-ID: demo"
```

### DELETE /v1/workspaces/{workspace_id}/entities/{entity_id}

Delete an entity. Query parameter `hard=true` for permanent deletion (default is soft delete).

```bash
curl -X DELETE "http://localhost:8080/v1/workspaces/abc12345/entities/actor-001?hard=false" \
  -H "X-Tenant-ID: demo"
```

---

## Relationships

Tag: **relationships** — Prefix: `/v1/workspaces/{workspace_id}/relationships`

Router file: `packages/api/src/dialectica_api/routers/relationships.py`

### GET /v1/workspaces/{workspace_id}/relationships

List edges with optional type filter.

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `edge_type` | string | `null` | Filter by edge type (e.g. `PARTY_TO`) |
| `limit` | int | `100` | Max results (max 1000) |

**Response:** `list[EdgeResponse]`

| Field | Type | Description |
|---|---|---|
| `id` | string | Edge identifier |
| `type` | string | Edge type from ontology |
| `source_id` | string | Source node ID |
| `target_id` | string | Target node ID |
| `properties` | object | Edge properties |
| `weight` | float | Edge weight (default 1.0) |

```bash
curl "http://localhost:8080/v1/workspaces/abc12345/relationships?edge_type=PARTY_TO" \
  -H "X-Tenant-ID: demo"
```

### DELETE /v1/workspaces/{workspace_id}/relationships/{edge_id}

Delete a relationship. Returns `204 No Content`.

```bash
curl -X DELETE http://localhost:8080/v1/workspaces/abc12345/relationships/edge-001 \
  -H "X-Tenant-ID: demo"
```

---

## Graph

Tag: **graph** — Prefix: `/v1/workspaces/{workspace_id}/graph`

Router file: `packages/api/src/dialectica_api/routers/graph.py`

### GET /v1/workspaces/{workspace_id}/graph

Return the full workspace graph (nodes + edges).

**Query parameters:** `limit` (int, default 200, max 1000) — caps node count.

**Response:** `{ "nodes": [...], "edges": [...] }`

```bash
curl "http://localhost:8080/v1/workspaces/abc12345/graph?limit=100" \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/graph/stats

Get graph statistics: total nodes/edges, type-level counts.

**Response:** `GraphStatsResponse`

| Field | Type | Description |
|---|---|---|
| `workspace_id` | string | Workspace identifier |
| `total_nodes` | int | Total node count |
| `total_edges` | int | Total edge count |
| `node_type_counts` | object | Counts per node type |
| `edge_type_counts` | object | Counts per edge type |

```bash
curl http://localhost:8080/v1/workspaces/abc12345/graph/stats \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/graph/subgraph

Get an N-hop subgraph centered on a node.

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `center_id` | string | *(required)* | Center node ID |
| `hops` | int | `2` | Traversal depth (1-4) |

**Response:** `SubgraphResponse` with `center_id`, `nodes`, `edges`, `hops`.

```bash
curl "http://localhost:8080/v1/workspaces/abc12345/graph/subgraph?center_id=actor-001&hops=2" \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/graph/search

Semantic/keyword search across the workspace graph. Attempts vector search first, falls back to keyword matching.

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `q` | string | *(required)* | Search query (min 1 char) |
| `limit` | int | `20` | Max results (max 100) |

**Response:** `list[SearchResult]` with `node_id`, `label`, `name`, `score`.

```bash
curl "http://localhost:8080/v1/workspaces/abc12345/graph/search?q=sanctions&limit=10" \
  -H "X-Tenant-ID: demo"
```

### POST /v1/workspaces/{workspace_id}/graph/query

Execute a raw GQL/Cypher query. **Admin only.**

**Request body:** `{ "query": "<cypher or GQL string>" }`

**Response:** `{ "result": ..., "query": "..." }`

```bash
curl -X POST http://localhost:8080/v1/workspaces/abc12345/graph/query \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: admin" \
  -H "X-Admin-Key: $ADMIN_API_KEY" \
  -d '{"query": "MATCH (a:Actor) RETURN a.name LIMIT 10"}'
```

---

## Extraction

Tag: **extraction** — Prefix: `/v1/workspaces/{workspace_id}`

Router file: `packages/api/src/dialectica_api/routers/extraction.py`

### POST /v1/workspaces/{workspace_id}/extract

Extract conflict entities from text and add to the workspace graph. Returns `202 Accepted`.

**Request body:** `ExtractRequest`

| Field | Type | Default | Description |
|---|---|---|---|
| `text` | string | *(required)* | Source text to extract from |
| `source_url` | string | `""` | URL provenance |
| `source_title` | string | `""` | Document title |
| `tier` | string | `"standard"` | Ontology tier for extraction |

**Response:** `ExtractionJob`

| Field | Type | Description |
|---|---|---|
| `job_id` | string | Unique job identifier |
| `workspace_id` | string | Target workspace |
| `status` | string | `pending`, `running`, `complete`, or `failed` |
| `created_at` | string | ISO-8601 timestamp |
| `completed_at` | string or null | Completion timestamp |
| `nodes_extracted` | int | Number of nodes created |
| `edges_extracted` | int | Number of edges created |
| `error` | string or null | Error message if failed |

```bash
curl -X POST http://localhost:8080/v1/workspaces/abc12345/extract \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"text": "Iran and the P5+1 reached an agreement...", "tier": "standard"}'
```

### POST /v1/workspaces/{workspace_id}/extract/document

Extract conflict entities from an uploaded document file. Returns `202 Accepted`.

**Request:** Multipart form upload with `file` field and optional `tier` query parameter.

```bash
curl -X POST http://localhost:8080/v1/workspaces/abc12345/extract/document \
  -H "X-Tenant-ID: demo" \
  -F "file=@report.txt" \
  -F "tier=full"
```

### GET /v1/workspaces/{workspace_id}/extractions

List all extraction jobs for a workspace.

**Response:** `list[ExtractionJob]`

```bash
curl http://localhost:8080/v1/workspaces/abc12345/extractions \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/extractions/{job_id}

Get the status of a specific extraction job.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/extractions/a1b2c3d4 \
  -H "X-Tenant-ID: demo"
```

---

## Theory

Tag: **theory** — Router file: `packages/api/src/dialectica_api/routers/theory.py`

### GET /v1/theory/frameworks

List all 15 conflict theory frameworks.

**Response:** `list[dict]` — framework metadata loaded from `data/seed/frameworks.json`.

```bash
curl http://localhost:8080/v1/theory/frameworks -H "X-Tenant-ID: demo"
```

### GET /v1/theory/frameworks/{framework_id}

Get a specific framework by its ID. Returns `404` if not found.

```bash
curl http://localhost:8080/v1/theory/frameworks/glasl -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/theory

Apply all 15 theory frameworks to a workspace and rank by applicability. Invokes the `TheoristAgent` from the reasoning package.

**Response:**

| Field | Type | Description |
|---|---|---|
| `workspace_id` | string | Workspace analysed |
| `top_framework` | string | Most applicable framework |
| `synthesis` | string | Cross-framework synthesis narrative |
| `assessments` | list | Per-framework results (see below) |

Each assessment contains: `framework_id`, `name`, `applicability` (0.0-1.0), `insights` (list), `indicators_present` (list).

```bash
curl http://localhost:8080/v1/workspaces/abc12345/theory \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/theory/{framework_id}

Apply a specific framework to the workspace. Response adds `limitations` field.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/theory/glasl \
  -H "X-Tenant-ID: demo"
```

---

## Reasoning

Tag: **reasoning** — Prefix: `/v1/workspaces/{workspace_id}`

Router file: `packages/api/src/dialectica_api/routers/reasoning.py`

### POST /v1/workspaces/{workspace_id}/analyze

Streaming conflict analysis. Returns Server-Sent Events (SSE).

**Request body:** `AnalyzeRequest`

| Field | Type | Default | Description |
|---|---|---|---|
| `query` | string | *(required)* | Analysis question |
| `mode` | string | `"general"` | Analysis mode |
| `top_k` | int | `20` | Number of context nodes to retrieve |
| `hops` | int | `2` | Graph traversal depth |

**Response:** `text/event-stream` with event types: `started`, `retrieval`, `symbolic`, `synthesis`, `complete`.

```bash
curl -N -X POST http://localhost:8080/v1/workspaces/abc12345/analyze \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"query": "What are the main escalation drivers?", "mode": "general"}'
```

### GET /v1/workspaces/{workspace_id}/escalation

Get Glasl escalation assessment: current stage (1-9), level (win-win / win-lose / lose-lose), escalation signals, intervention recommendation, and trajectory forecast.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/escalation \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/ripeness

Get Zartman ripeness assessment: MHS score, MEO score, overall score, ripeness boolean, and contributing factors.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/ripeness \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/power

Get French/Raven power map: dyad power scores, asymmetries, most powerful actor, and recommendations.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/power \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/trust

Get Mayer/Davis/Schoorman trust matrix: per-dyad ability/benevolence/integrity scores, overall averages, and recent trust change events.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/trust \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/causation

Get causal chain analysis: chains with root events, depth, cycle detection, and identified root causes with downstream impact counts.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/causation \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/quality

Get graph quality metrics: completeness score, consistency score, coverage score, missing node types, orphan count, and actionable recommendations.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/quality \
  -H "X-Tenant-ID: demo"
```

### GET /v1/workspaces/{workspace_id}/network

Get network topology metrics: centrality rankings (betweenness, closeness, degree), community detection, polarisation level (modularity), and broker identification with mediation potential scores.

```bash
curl http://localhost:8080/v1/workspaces/abc12345/network \
  -H "X-Tenant-ID: demo"
```

---

## Developers

Tag: **developers** — Prefix: `/v1/developers`

Router file: `packages/api/src/dialectica_api/routers/developers.py`

### POST /v1/developers/keys

Create a new API key for the current tenant.

**Request body:** `ApiKeyCreate`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | *(required)* | Key display name |
| `rate_limit_per_min` | int | `100` | Rate limit per minute |

**Response (201):** `ApiKeyResponse` with `key_id`, `name`, `api_key`, `tenant_id`, `created_at`, `rate_limit_per_min`.

```bash
curl -X POST http://localhost:8080/v1/developers/keys \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"name": "my-integration", "rate_limit_per_min": 60}'
```

### GET /v1/developers/keys

List all API keys for the current tenant.

```bash
curl http://localhost:8080/v1/developers/keys -H "X-Tenant-ID: demo"
```

### DELETE /v1/developers/keys/{key_id}

Delete an API key. Returns `204 No Content`.

```bash
curl -X DELETE http://localhost:8080/v1/developers/keys/abc123 \
  -H "X-Tenant-ID: demo"
```

### GET /v1/developers/usage

Get API usage statistics for the current tenant.

```bash
curl http://localhost:8080/v1/developers/usage -H "X-Tenant-ID: demo"
```

---

## Admin

Tag: **admin** — Prefix: `/v1/admin`

Router file: `packages/api/src/dialectica_api/routers/admin.py`

All admin endpoints require the `X-Admin-Key` header.

### GET /v1/admin/system

Get system information: graph backend, API version, environment.

**Response:** `SystemInfo`

```bash
curl http://localhost:8080/v1/admin/system \
  -H "X-Tenant-ID: admin" \
  -H "X-Admin-Key: $ADMIN_API_KEY"
```

### GET /v1/admin/usage

Get API usage statistics across all tenants.

```bash
curl http://localhost:8080/v1/admin/usage \
  -H "X-Tenant-ID: admin" \
  -H "X-Admin-Key: $ADMIN_API_KEY"
```

### POST /v1/admin/seed

Trigger seed data loading (runs `scripts/seed_sample_data.py` as a subprocess).

```bash
curl -X POST http://localhost:8080/v1/admin/seed \
  -H "X-Tenant-ID: admin" \
  -H "X-Admin-Key: $ADMIN_API_KEY"
```

---

## Error Responses

All endpoints use standard HTTP status codes:

| Status | Meaning |
|---|---|
| `200` | Success |
| `201` | Created |
| `202` | Accepted (async job started) |
| `204` | No Content (successful deletion) |
| `400` | Bad request (invalid query or missing field) |
| `403` | Access denied (tenant mismatch) |
| `404` | Resource not found |
| `503` | Graph client unavailable |

Error responses follow the format: `{ "detail": "Error message" }`.

---

## Source Files

| Router | File |
|---|---|
| health | `packages/api/src/dialectica_api/routers/health.py` |
| workspaces | `packages/api/src/dialectica_api/routers/workspaces.py` |
| entities | `packages/api/src/dialectica_api/routers/entities.py` |
| relationships | `packages/api/src/dialectica_api/routers/relationships.py` |
| graph | `packages/api/src/dialectica_api/routers/graph.py` |
| extraction | `packages/api/src/dialectica_api/routers/extraction.py` |
| theory | `packages/api/src/dialectica_api/routers/theory.py` |
| reasoning | `packages/api/src/dialectica_api/routers/reasoning.py` |
| developers | `packages/api/src/dialectica_api/routers/developers.py` |
| admin | `packages/api/src/dialectica_api/routers/admin.py` |
