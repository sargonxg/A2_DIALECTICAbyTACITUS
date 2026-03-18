# Cross-Product Migration Guide

How to converge each TACITUS product onto DIALECTICA as the shared backend.

---

## Compass → DIALECTICA

### Current State
Compass runs its own Gemini-based extraction inline within the frontend/backend to parse conflict documents and display entity graphs.

### Target State
Compass calls DIALECTICA API endpoints for extraction and graph retrieval. All entity resolution, tier-based filtering, and theory assessment happen server-side in DIALECTICA.

### Migration Steps

1. **Replace inline Gemini extraction with DIALECTICA extraction endpoint.**
   Remove the direct Gemini API calls. Instead, create a workspace per analysis session and call:
   ```
   POST /v1/workspaces/{workspace_id}/extract
   ```
   Pass the raw document text in the request body. DIALECTICA runs the same Gemini extraction but normalizes output into the 15-node ontology.

2. **Read results via the graph endpoint.**
   After extraction completes, retrieve the full conflict graph:
   ```
   GET /v1/workspaces/{workspace_id}/graph
   GET /v1/workspaces/{workspace_id}/entities?node_type=Actor
   ```

3. **Install and use the TypeScript SDK.**
   Use `@tacitus/dialectica-sdk` for typed request/response handling. The SDK wraps all endpoints and provides TypeScript interfaces matching the ontology models.

4. **Map Compass UI components to DIALECTICA node types.**
   - Actor cards → `Actor` nodes
   - Relationship arrows → `ConflictRelationship` edges (PARTY_TO, ALLIED_WITH, OPPOSED_TO, etc.)
   - Timeline entries → `Event` nodes
   - Issue tags → `Issue` and `Interest` nodes

5. **Use the tier system for progressive detail.**
   Compass can request `essential` tier for overview dashboards (Actor, Conflict, Event, Issue, Interest) and `full` tier when the user drills into a conflict for all 15 node types.

6. **Leverage theory endpoints for analysis panels.**
   Replace any custom scoring with:
   ```
   POST /v1/workspaces/{workspace_id}/theory/assess
   ```

---

## PRAXIS → DIALECTICA

### Current State
PRAXIS uses mock/static graph data to drive its simulation and scenario-planning interface. Graph structures are hardcoded or generated from templates.

### Target State
PRAXIS reads live conflict graphs from DIALECTICA and uses DIALECTICA reasoning endpoints for analysis. Simulation parameters map to theory framework `assess()` calls.

### Migration Steps

1. **Replace mock data with DIALECTICA graph calls.**
   Remove static JSON fixtures. Instead, fetch real graphs:
   ```
   GET /v1/workspaces/{workspace_id}/graph
   GET /v1/workspaces/{workspace_id}/entities
   GET /v1/workspaces/{workspace_id}/relationships
   ```

2. **Use reasoning endpoints for conflict analysis.**
   Replace any inline heuristics with:
   ```
   POST /v1/workspaces/{workspace_id}/reasoning/analyze
   GET  /v1/workspaces/{workspace_id}/graph/network_metrics
   ```

3. **Map simulation parameters to theory `assess()` calls.**
   Each PRAXIS simulation dimension corresponds to a DIALECTICA theory framework:
   - Escalation level → `GlaslFramework.assess()`
   - Power balance → `FrenchRavenFramework.assess()`
   - Trust dynamics → `MayerTrustFramework.assess()`
   - Emotional climate → `PlutchikFramework.assess()`
   - Resolution readiness → `ZartmanFramework.assess()` (ripeness)

4. **Wire scenario branching to DIALECTICA workspaces.**
   Each PRAXIS scenario branch can be its own workspace. Clone a workspace, mutate parameters, then re-run theory assessments to compare outcomes.

5. **Use the SDK `info` endpoint to discover capabilities.**
   ```
   GET /v1/sdk/info
   ```
   This returns available node types, edge types, theory frameworks, and endpoint paths — useful for dynamically building PRAXIS UI controls.

---

## Wind Tunnel → DIALECTICA

### Current State
Wind Tunnel runs CiviSphere with its own Vertex AI pipeline to process survey data and compute polarization metrics. Moral Foundations Theory and Schwartz Values are applied via custom code.

### Target State
Wind Tunnel uses DIALECTICA extraction and reasoning for survey analysis. Survey inputs flow through workspaces, and polarization is computed via DIALECTICA network metrics.

### Migration Steps

1. **Route survey input through DIALECTICA workspaces.**
   Each survey batch or cohort becomes a workspace:
   ```
   POST /v1/workspaces
   POST /v1/workspaces/{workspace_id}/extract
   ```
   Pass survey free-text responses as documents for extraction.

2. **Map Moral Foundations and Schwartz Values to DIALECTICA node types.**
   - Moral foundations (Care, Fairness, Loyalty, Authority, Sanctity) → `Interest` nodes with `interest_type` set appropriately
   - Schwartz values (Universalism, Benevolence, Conformity, etc.) → `Narrative` nodes with `narrative_type: value_claim`
   - Value conflicts → `Conflict` nodes linking opposing `Interest` pairs via `OPPOSED_TO` edges

3. **Compute polarization via network metrics.**
   Replace custom polarization calculations with:
   ```
   GET /v1/workspaces/{workspace_id}/graph/network_metrics
   ```
   The response includes clustering coefficients, modularity scores, and faction detection that map directly to polarization indices.

4. **Use theory frameworks for value-conflict analysis.**
   - `GaltungFramework.assess()` → structural vs. direct violence patterns
   - `DeutschFramework.assess()` → cooperative vs. competitive orientation
   - `BurtonFramework.assess()` → basic human needs satisfaction

5. **Replace Vertex AI pipeline with DIALECTICA extraction.**
   The `ExtractionPipeline` in `dialectica-extraction` handles Gemini calls, entity resolution, and graph construction. No separate Vertex AI setup needed.

---

## ARGUS → DIALECTICA

### Current State
ARGUS runs its own LightRAG-based extraction pipeline to process documents, build knowledge graphs, and support retrieval-augmented generation.

### Target State
ARGUS uses `dialectica-extraction` as a library for entity extraction and graph construction, and leverages DIALECTICA's GraphRAG retriever for retrieval.

### Migration Steps

1. **Replace custom extraction with `ExtractionPipeline`.**
   Remove the LightRAG extraction code. Import and configure DIALECTICA's pipeline:
   ```python
   from dialectica_extraction.pipeline import ExtractionPipeline

   pipeline = ExtractionPipeline(config=extraction_config)
   result = await pipeline.extract(document_text, tier="full")
   ```
   This returns typed `ConflictNode` and `ConflictRelationship` objects conforming to the 15-node ontology.

2. **Route document processing through DIALECTICA workspaces.**
   Each ARGUS document collection maps to a workspace:
   ```
   POST /v1/workspaces
   POST /v1/workspaces/{workspace_id}/extract
   ```
   Bulk document ingestion is supported via repeated extract calls against the same workspace.

3. **Replace custom RAG with DIALECTICA GraphRAG retriever.**
   Instead of LightRAG's vector-only retrieval, use DIALECTICA's graph-aware retrieval:
   ```
   POST /v1/workspaces/{workspace_id}/reasoning/query
   ```
   This combines vector similarity with graph traversal for contextually richer retrieval.

4. **Map ARGUS entity types to DIALECTICA ontology.**
   - People/organizations → `Actor`
   - Events/incidents → `Event`
   - Claims/assertions → `Narrative`
   - Sources/documents → `Evidence`
   - Causal links → `CAUSED` edges
   - Attribution → `PARTICIPATES_IN` edges

5. **Use the tier system for extraction granularity.**
   - `essential` (5 types): Fast extraction for quick document triage
   - `standard` (10 types): Balanced extraction for most ARGUS workflows
   - `full` (15 types): Complete extraction for deep analysis

6. **Leverage DIALECTICA theory frameworks for intelligence analysis.**
   ```python
   POST /v1/workspaces/{workspace_id}/theory/assess
   {"framework": "pearl_causal"}
   ```
   Pearl Causal framework is particularly relevant for ARGUS counterfactual reasoning.

---

## SDK Discovery

All products can call `GET /v1/sdk/info` to dynamically discover:
- Available node types and edge types
- Supported extraction tiers
- Theory framework list
- Endpoint URL patterns

This enables forward-compatible integrations that adapt as the ontology evolves.
