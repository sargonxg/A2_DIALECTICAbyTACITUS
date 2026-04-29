# Terminal ingestion workflow

This is the practical beginner loop for making DIALECTICA useful as the TACITUS backbone.

```text
public/open text -> Gemini extraction -> Neo4j graph -> Databricks Delta mirror -> review queue -> validated TACITUS memory
```

## What you can run from terminal

### 1. Download open-source/public-domain text

Project Gutenberg examples:

```powershell
uv run python tools/download_gutenberg.py 1513 --output data/raw/romeo_juliet.txt --max-chars 30000
uv run python tools/download_gutenberg.py 2554 --output data/raw/crime_punishment.txt --max-chars 30000
uv run python tools/download_gutenberg.py 2600 --output data/raw/war_and_peace.txt --max-chars 30000
```

Recommended first test:

```powershell
uv run python tools/download_gutenberg.py 1513 --output data/raw/romeo_juliet_act1.txt --max-chars 30000
```

### 2. Ingest text into Neo4j

Set secrets for the current PowerShell session:

```powershell
$env:GEMINI_API_KEY = "your-rotated-key"
$env:NEO4J_URI = "neo4j+s://your-instance.databases.neo4j.io"
$env:NEO4J_USER = "neo4j"
$env:NEO4J_PASSWORD = "your-rotated-password"
$env:NEO4J_DATABASE = "neo4j"
```

Run a dry extraction first:

```powershell
uv run python tools/ingest_text_to_neo4j.py `
  data/raw/romeo_juliet_act1.txt `
  --workspace-id ws_romeo_act1 `
  --title "Romeo and Juliet Act 1" `
  --dry-run
```

If `data/extracted/ws_romeo_act1.json` looks reasonable, write to Neo4j:

```powershell
uv run python tools/ingest_text_to_neo4j.py `
  data/raw/romeo_juliet_act1.txt `
  --workspace-id ws_romeo_act1 `
  --title "Romeo and Juliet Act 1"
```

### 3. Query Neo4j from terminal

Use the Python-driver Cypher helper:

```powershell
uv run python tools/neo4j_cypher.py "MATCH (n:ConflictNode {workspace_id: 'ws_romeo_act1'}) RETURN n.label AS label, count(*) AS count ORDER BY count DESC"
```

Useful checks:

```powershell
uv run python tools/neo4j_cypher.py "MATCH (n:Actor {workspace_id: 'ws_romeo_act1'}) RETURN n.name, n.confidence ORDER BY n.confidence DESC"
uv run python tools/neo4j_cypher.py "MATCH (a)-[r]->(b) WHERE r.workspace_id = 'ws_romeo_act1' RETURN a.name, type(r), b.name, r.confidence LIMIT 25"
```

### 4. Push graph usage into Databricks

Save Databricks token profile, if not using OAuth:

```powershell
.\infrastructure\databricks\save_token_profile.ps1 `
  -Profile tacitus `
  -WorkspaceHost "https://YOUR-WORKSPACE.cloud.databricks.com"
```

Deploy the bundle:

```powershell
databricks bundle validate --profile tacitus
databricks bundle deploy --profile tacitus
```

Run low-cost operational loop:

```powershell
databricks bundle run tacitus_operational_loop --profile tacitus
```

Run KGE only later:

```powershell
databricks bundle run tacitus_kge_candidates_manual --profile tacitus
```

## Cost guardrails

The bundle currently:

- has no schedule,
- limits concurrent runs to one,
- has explicit timeouts,
- separates KGE into a manual-only job,
- tags jobs with `project=tacitus-dialectica`.

Check workspace/job status:

```powershell
.\infrastructure\databricks\check_usage.ps1 -Profile tacitus
```

Databricks budgets monitor usage and send alerts, but they do not stop charges. If you need a hard cap, set it in the cloud billing account too.

## What to inspect after each run

In Neo4j:

```cypher
MATCH (n:ConflictNode {workspace_id: 'ws_romeo_act1'})
RETURN n.label, count(*)
ORDER BY count(*) DESC;

MATCH (a)-[r]->(b)
WHERE r.workspace_id = 'ws_romeo_act1'
RETURN a.name, type(r), b.name, r.confidence
ORDER BY r.confidence ASC
LIMIT 25;
```

In Databricks:

```sql
SELECT * FROM dialectica.conflict_graphs.graph_quality_signals;
SELECT * FROM dialectica.conflict_graphs.review_queue ORDER BY severity DESC, confidence ASC;
SELECT * FROM dialectica.conflict_graphs.actor_features ORDER BY degree DESC;
```

## First serious TACITUS tests

1. `Romeo and Juliet` Act 1: family feud and escalation.
2. Melian Dialogue: coercive power and interests.
3. `Crime and Punishment` first chapters: norm violation and evidence ambiguity.
4. One UN resolution: norm extraction.
5. One TACITUS meeting note: real product memory.
