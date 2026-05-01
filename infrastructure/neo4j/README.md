# DIALECTICA Neo4j Graph Structure

Neo4j is the operational graph for TACITUS. Databricks snapshots this graph into
Delta tables for quality checks, feature generation, review queues, and optional
link prediction, but Neo4j remains the live query surface.

## Apply Schema

The current runtime schema files are:

- `dialectica_constraints.cypher`: canonical conflict graph constraints.
- `dynamic_graph_layers.cypher`: dynamic ontology and layered graph constraints.
- `graphops_runtime_schema.cypher`: GraphOps `TacitusCoreV1` runtime schema used
  by the web workbench graph-writeback engine.

Use environment variables or allow the script to prompt securely:

```powershell
$env:NEO4J_URI = "neo4j+s://..."
$env:NEO4J_USERNAME = "neo4j"
$env:NEO4J_DATABASE = "neo4j"
uv run python tools/apply_neo4j_schema.py
```

If applying manually in Neo4j Browser or Cypher Shell, run
`graphops_runtime_schema.cypher` after the base constraints so GraphOps writeback
has its workspace, case, extraction-run, primitive-type, review-status, and
full-text indexes.

Do not paste secrets into terminal commands. Let the password prompt collect the
password, or use a local secret manager.

## Graph Layers

Use one database with explicit labels and properties first. If volume or access
control demands it later, split these layers into separate databases or named
graphs.

| Layer | Labels | Purpose |
| --- | --- | --- |
| Source graph | `Document`, `Chunk`, `Evidence` | Preserve provenance, quote snippets, licensing, and reliability. |
| Situation graph | `ConflictNode`, plus the 15 TACITUS ontology labels | Store actors, conflicts, events, issues, interests, norms, processes, outcomes, narratives, power, trust, emotion, places, evidence, and roles. |
| Ontology graph | `OntologyType`, `TheoryFrameworkNode` | Explain the grammar and theory behind every extraction. |
| Reasoning graph | `ReasoningTrace`, `InferredFact`, `OperationalSignal` | Store symbolic rules, Databricks outputs, contradictions, and review status. |
| Activity graph | `User`, `Project`, `Workspace`, `ReviewDecision` | Track analyst action, approval, correction, and model feedback. |

## Required Properties

Every extracted ontology node should carry:

```text
id, label, workspace_id, tenant_id, name, confidence, source, source_quote, created_at
```

Every relationship should carry:

```text
id, workspace_id, tenant_id, confidence, source_quote, extraction_method, created_at
```

## First Queries

```cypher
MATCH (c:ConflictNode:Conflict {workspace_id: $workspace_id})
RETURN c.name, c.status, c.glasl_stage
ORDER BY coalesce(c.glasl_stage, 0) DESC;
```

```cypher
MATCH (a:ConflictNode:Actor)-[r:HAS_POWER_OVER]->(b:ConflictNode:Actor)
WHERE a.workspace_id = $workspace_id
RETURN a.name, b.name, r.domain, r.magnitude, r.confidence
ORDER BY coalesce(r.magnitude, 0) DESC;
```

```cypher
MATCH (e:ConflictNode:Event)-[v:VIOLATES]->(n:ConflictNode:Norm)
OPTIONAL MATCH (e)-[:EVIDENCED_BY]->(ev:ConflictNode:Evidence)
WHERE e.workspace_id = $workspace_id
RETURN e.name, n.name, v.severity, collect(ev.name)[0..5] AS evidence;
```
