# DIALECTICA Runtime Secrets and Operations

This document tracks the runtime connections needed for the GraphOps control plane.

## Current Hosting

The public protected console is deployed on Vercel:

- `https://dialectica.tacitus.me/graphops`

The Databricks workspace is live and used for bundle jobs, Delta tables, and staged pipeline artifacts.

Google Cloud project checked:

- `praxisbytacitus`

## GCP Secret Manager

Secret containers created in `praxisbytacitus`:

- `dialectica-neo4j-uri`
- `dialectica-neo4j-username`
- `dialectica-neo4j-password`
- `dialectica-neo4j-database`
- `dialectica-gemini-api-key`
- `dialectica-databricks-host`
- `dialectica-databricks-token`
- `dialectica-neo4j-client-id`
- `dialectica-neo4j-client-secret`

These are containers. Add or rotate secret versions without printing values:

```powershell
Set-Content -LiteralPath .secret.tmp -Value $env:NEO4J_URI -NoNewline
gcloud secrets versions add dialectica-neo4j-uri --project=praxisbytacitus --data-file=.secret.tmp
Remove-Item -LiteralPath .secret.tmp -Force
```

Use the same pattern for other values. Do not paste production secrets into source files or shell history.

## Vercel Runtime Env

The Vercel app expects:

- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `DATABRICKS_WAREHOUSE_ID`
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `NEO4J_DATABASE`
- `GEMINI_API_KEY`
- `GRAPHOPS_BASIC_AUTH_USER`
- `GRAPHOPS_BASIC_AUTH_PASSWORD`

Neo4j write/query paths remain server-side only.

## Databricks Secret Scope

Databricks jobs that write to Neo4j expect the `tacitus` secret scope to contain:

- `neo4j-uri`
- `neo4j-username`
- `neo4j-password`
- `neo4j-database`
- optionally `gemini-api-key`

## Operational Flow

1. User opens `/graphops`.
2. User runs an AI configuration command.
3. Aletheia proposes a workspace template, dynamic ontology, graph layers, rules, and benchmarks.
4. User creates a pipeline plan.
5. Pipeline plan is staged to Databricks Workspace files.
6. Databricks `pipeline-artifact-ingestion` normalizes plans into Delta tables.
7. Source ingestion and extraction jobs produce candidates.
8. Accepted graph facts write to Neo4j.
9. GraphOps query and rule APIs produce graph-grounded answers and benchmarks.

## Current Blockers

- Vercel does not yet have Neo4j production secrets bound.
- Databricks `tacitus` secret scope still needs Neo4j values before writeback.
- The SQL warehouse count query may fall back to configured metadata when a new table is temporarily unavailable or the warehouse query fails.

## Safe Runtime Principle

AI may propose:

- ontology extensions;
- extraction targets;
- rules;
- benchmark plans;
- graph questions.

AI must not silently promote unverified claims to graph truth. Every fact needs provenance, confidence, source scope, extraction run, and review status.
