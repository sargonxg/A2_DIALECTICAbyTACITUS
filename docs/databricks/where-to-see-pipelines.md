# Where to See TACITUS Databricks Pipelines

Workspace:

```text
https://dbc-69e04818-40fb.cloud.databricks.com/jobs?o=7474658425841042
```

After deployment, open **Workflows > Jobs** and search for:

| Job | Purpose | Cost posture |
| --- | --- | --- |
| `[dev giulio] tacitus-dialectica-book-ai-extraction-demo` | Open book chunks to Databricks AI extraction candidates | Low-cost demo, already run successfully |
| `tacitus_operational_loop` | Neo4j snapshot, Delta tables, graph quality, review queue | Low-cost, manual run by default |
| `tacitus_kge_candidates_manual` | KGE/link prediction candidates from Delta edges | Manual expensive experiment |
| `tacitus_neurosymbolic_benchmark_manual` | Baseline LLM vs DIALECTICA graph-grounded benchmark | Manual benchmark |

Current deployed job IDs:

| Job ID | Name |
| --- | --- |
| `136658630245751` | `[dev giulio] tacitus-dialectica-book-ai-extraction-demo` |
| `261036137711214` | `[dev giulio] tacitus-dialectica-complex-book-graph-demo` |
| `958424080973640` | `[dev giulio] tacitus-dialectica-operational-loop` |
| `278369455996320` | `[dev giulio] tacitus-dialectica-neurosymbolic-benchmark-manual` |
| `921155103888424` | `[dev giulio] tacitus-dialectica-kge-candidates-manual` |

Successful demo run:

```text
https://dbc-69e04818-40fb.cloud.databricks.com/?o=7474658425841042#job/136658630245751/run/227559218086552
```

It created:

| Table | Rows observed |
| --- | --- |
| `dialectica.conflict_graphs.raw_text_chunks` | 35 |
| `dialectica.conflict_graphs.ai_extraction_candidates` | 35 |

Complex book demo run:

```text
https://dbc-69e04818-40fb.cloud.databricks.com/?o=7474658425841042#job/261036137711214/run/795929402349644
```

Sources:

- War and Peace (`2600`)
- Crime and Punishment (`2554`)
- The Federalist Papers (`1404`)

Workspace:

```text
books-complex-conflict-lab
```

Observed after successful run:

| Table | Rows observed |
| --- | --- |
| `dialectica.conflict_graphs.raw_text_chunks` | 333 |
| `dialectica.conflict_graphs.ai_extraction_candidates` | 275 |
| `dialectica.conflict_graphs.ontology_profile_coverage` | 4 |
| `dialectica.conflict_graphs.source_reliability_signals` | 3 |
| `dialectica.conflict_graphs.temporal_event_signals` | 3 |
| `dialectica.conflict_graphs.claim_review_queue` | 216 |

Current complex demo tasks:

| Task | Notebook | Output |
| --- | --- | --- |
| `seed_complex_books` | `notebooks/databricks/00_seed_open_books_to_delta.py` | Public-domain source chunks |
| `ai_extract_complex_chunks` | `notebooks/databricks/00_ai_extract_chunks_to_delta.py` | TACITUS ontology candidates |
| `dynamic_ontology_quality` | `notebooks/databricks/05_dynamic_ontology_quality_and_profiles.py` | Profile coverage, source reliability, temporal signals, claim review queue |

Each run has task tabs:

| Task | Notebook | Output |
| --- | --- | --- |
| `neo4j_delta_snapshot` | `notebooks/databricks/01_neo4j_delta_operational_signals.py` | Delta nodes, edges, actor features, graph quality signals |
| `build_review_queue` | `notebooks/databricks/02_review_queue.py` | Analyst queue for low-confidence edges and missing evidence |
| `kge_link_candidates` | `notebooks/databricks/03_kge_from_delta_link_predictions.py` | Candidate missing links, manual-only |

The main tables are expected under:

```text
Catalog: dialectica
Schema: conflict_graphs
Tables:
  nodes_bronze
  edges_bronze
  actor_features
  graph_quality_signals
  review_queue
  kge_link_candidates
  benchmark_items
  benchmark_prompts
  benchmark_answers
  benchmark_judgments
```

## Deploy From Terminal

Authenticate safely first. Prefer OAuth:

```powershell
infrastructure\databricks\setup_cli.ps1 -Profile tacitus -WorkspaceHost "https://dbc-69e04818-40fb.cloud.databricks.com" -SkipSecrets
```

Or save a token without putting it in command history:

```powershell
infrastructure\databricks\save_token_profile.ps1 -Profile tacitus -WorkspaceHost "https://dbc-69e04818-40fb.cloud.databricks.com"
```

Then add Databricks secrets. The script prompts for secrets and does not require
putting them in shell history:

```powershell
infrastructure\databricks\setup_cli.ps1 -Profile tacitus -WorkspaceHost "https://dbc-69e04818-40fb.cloud.databricks.com" -SkipLogin
```

Validate and deploy:

```powershell
databricks bundle validate -t dev --profile tacitus
databricks bundle deploy -t dev --profile tacitus
databricks bundle run tacitus_operational_loop -t dev --profile tacitus
```

If `databricks` is not on PATH in the current shell, use:

```powershell
& "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Databricks.DatabricksCLI_Microsoft.Winget.Source_8wekyb3d8bbwe\databricks.exe" bundle validate -t dev --profile tacitus
```

## $100 Budget Guardrail

Databricks budgets are alerts, not hard stops. Keep the experiment under control by:

1. Leaving both jobs manual until the graph works.
2. Running `tacitus_operational_loop` only after new ingestion batches.
3. Running `tacitus_kge_candidates_manual` only on small edge samples.
4. Tagging every job with `project=tacitus-dialectica`.
5. Creating an account budget alert for 100 USD and a cloud-provider budget alert too.
6. Stopping all-purpose clusters; use job/serverless compute only when needed.

## What I Still Need

To deploy from this terminal, I need you to run one of the authentication scripts
interactively, or provide a fresh token through the script prompt. The token
previously pasted in chat should be rotated because it is now exposed.
