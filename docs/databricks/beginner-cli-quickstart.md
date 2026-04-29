# Beginner CLI quickstart

This is the terminal-first path for running DIALECTICA as the TACITUS backbone with Neo4j + Databricks.

## What works now

- The repository installs with `uv sync --all-packages`.
- The Databricks connector unit tests pass.
- The ontology primitive tests pass.
- Three Databricks notebooks compile locally.
- A Databricks bundle exists at `databricks.yml`.
- A PowerShell setup helper exists at `infrastructure/databricks/setup_cli.ps1`.

## What does not exist yet

- Docker is not installed on this machine, so local Docker Compose is not the fastest path.
- The docs mention `/v1/admin/databricks/test`, but that API route is not implemented yet.
- The production-grade API-to-Databricks bridge is still a stub; the practical path is Databricks notebooks/jobs reading Neo4j directly.

## Step 0: rotate secrets

Credentials pasted into chat must be considered exposed. Rotate:

- Gemini API key.
- Neo4j Aura password.

Use the rotated values in the setup script.

## Step 1: open PowerShell in the repo

```powershell
cd C:\Users\giuli\CODEX\A2_DIALECTICAbyTACITUS
```

## Step 2: install dependencies

```powershell
uv sync --all-packages
```

## Step 3: set up Databricks CLI, login, and secrets

If you have a Databricks access token instead of browser OAuth, save it without exposing it in shell history:

```powershell
.\infrastructure\databricks\save_token_profile.ps1 `
  -Profile tacitus `
  -WorkspaceHost "https://YOUR-WORKSPACE.cloud.databricks.com"
```

The script prompts for the token securely and writes profile `tacitus` to `~\.databrickscfg`.

If you know your Databricks workspace URL:

```powershell
.\infrastructure\databricks\setup_cli.ps1 `
  -Profile tacitus `
  -WorkspaceHost "https://YOUR-WORKSPACE.cloud.databricks.com"
```

If you do not know the workspace URL:

```powershell
.\infrastructure\databricks\setup_cli.ps1 -Profile tacitus
```

The CLI opens a browser login. After login, the script creates secret scope `tacitus` and prompts for:

```text
neo4j-uri
neo4j-user
neo4j-password
neo4j-database
gemini-api-key
```

## Step 4: validate the Databricks bundle

The setup script already runs validation. You can repeat it:

```powershell
databricks bundle validate --profile tacitus
```

## Step 5: deploy the jobs

```powershell
databricks bundle deploy --profile tacitus
```

This deploys:

```text
tacitus-dialectica-operational-loop
tacitus-dialectica-kge-candidates-manual
```

The default operational loop is low-cost and only mirrors the graph plus builds the review queue. KGE is separated because model training is more expensive.

## Step 6: run the low-cost job

```powershell
databricks bundle run tacitus_operational_loop --profile tacitus
```

The job runs:

1. `01_neo4j_delta_operational_signals.py`
2. `02_review_queue.py`

Run KGE only after the graph has enough edges and the review queue looks sane:

```powershell
databricks bundle run tacitus_kge_candidates_manual --profile tacitus
```

## Step 6.5: cost guardrails

The bundle has these guardrails:

- no schedule by default,
- max one concurrent run,
- short job/task timeouts,
- KGE split into a separate manual job,
- tags for budget tracking: `project=tacitus-dialectica`.

Check the workspace profile and job inventory:

```powershell
.\infrastructure\databricks\check_usage.ps1 -Profile tacitus
```

To download account billable usage, you need an account-level Databricks profile with account admin permission:

```powershell
.\infrastructure\databricks\check_usage.ps1 `
  -Profile tacitus `
  -AccountProfile YOUR_ACCOUNT_PROFILE
```

Databricks budgets are alerts, not hard stops. For a real spending cap, also create a budget/alert in the cloud billing account.

## Step 7: first test data

Use this sequence:

1. Repo sample data from `data/seed/samples`.
2. `Romeo and Juliet` Act 1.
3. Melian Dialogue from Thucydides.
4. One UN Security Council resolution.
5. One TACITUS internal note/interview/transcript.

## Terminal commands you will use most

```powershell
databricks auth profiles
databricks current-user me --profile tacitus
databricks secrets list-scopes --profile tacitus
databricks secrets list-secrets tacitus --profile tacitus
databricks bundle validate --profile tacitus
databricks bundle deploy --profile tacitus
databricks bundle run tacitus_operational_loop --profile tacitus
```

## Beginner mental model

Neo4j is the live graph.

Databricks is the operating room:

- copy graph into Delta,
- inspect quality,
- create review queues,
- train link-prediction candidates,
- send only validated signals back.

Gemini is the extractor/summarizer, not the source of truth.

Human validation decides what becomes TACITUS memory.
