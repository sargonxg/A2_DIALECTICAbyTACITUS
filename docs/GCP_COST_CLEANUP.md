# GCP Cost Cleanup

Last updated: 2026-05-03

## Current Cost-Saver Policy

- Use one deployment region: `us-central1`.
- Cloud Run defaults to `min-instances=0`, `max-instances=1`, CPU throttling on,
  startup CPU boost off.
- Use external Neo4j as the only durable graph store for Dialectica.
- Use one small Cloud SQL PostgreSQL instance as the durable API metadata and
  graph reasoning audit/control plane when production run history is needed.
- Keep Cozo as an in-memory, rebuildable Cloud Run mirror.
- Do not provision Spanner, Redis, BigQuery, Vertex endpoints, or Databricks for
  the minimal Dialectica backend. Databricks remains optional for batch/lakehouse
  scale; ingestion must still work directly through the API without it.

Cloud Run can idle at zero. Cloud SQL cannot: it has storage and instance cost
unless stopped. For cost-saving environments, use the smallest non-HA instance,
avoid read replicas, and stop it when durable audit history is not needed.

## Live Audit: `praxisbytacitus`

Actions applied on 2026-05-01:

- Set all Cloud Run services in `us-central1` to effective `min=0`, `max=1`,
  CPU throttling on, startup CPU boost off:
  - `gdelt-poller`
  - `on-document-uploaded`
  - `on-situation-created`
  - `praxis-backend`
  - `praxis-frontend`
- Paused all Cloud Scheduler jobs in `us-central1`:
  - `praxis-check-alerts`
  - `praxis-generate-briefing`
  - `gdelt-poller`

Remaining known idle-cost source:

- Cloud SQL `praxisbytacitus-instance` in `us-east4` is still
  `activationPolicy=ALWAYS`. It was not stopped because `praxis-backend`
  currently points at it for Postgres/LangGraph checkpoint state.

Dialectica production should consolidate onto a single Cloud SQL instance for:

- API metadata
- pipeline runs
- source chunks
- dynamic ontology profile records
- graph object/edge audit mirrors

Do not create separate Cloud SQL instances for Graphiti, Cozo, Databricks, or
frontend state.

Large storage source:

- Artifact Registry repository `praxis` had roughly tens of GB of image
  manifests/layers. Clean old images after protecting current Cloud Run image
  digests.

## Audit

```powershell
.\infrastructure\scripts\gcp-cost-audit.ps1 -ProjectId praxisbytacitus -Region us-central1
```

Review these first because they can create idle spend:

- Cloud SQL instances with `activationPolicy=ALWAYS`
- Spanner instances
- Redis instances
- Compute disks or reserved IP addresses
- Vertex AI endpoints or deployed indexes
- Cloud Scheduler jobs that wake services
- Large Artifact Registry repositories

## Reversible Consolidation

Dry run:

```powershell
.\infrastructure\scripts\gcp-cost-consolidate.ps1 -ProjectId praxisbytacitus -Region us-central1
```

Apply Cloud Run cold-start settings:

```powershell
.\infrastructure\scripts\gcp-cost-consolidate.ps1 -ProjectId praxisbytacitus -Region us-central1 -Apply
```

Apply Cloud Run settings and pause scheduled jobs:

```powershell
.\infrastructure\scripts\gcp-cost-consolidate.ps1 -ProjectId praxisbytacitus -Region us-central1 -Apply -PauseSchedulers
```

Stop Cloud SQL only when the app can tolerate losing API metadata writes,
checkpointing, and graph reasoning run history:

```powershell
.\infrastructure\scripts\gcp-cost-consolidate.ps1 -ProjectId praxisbytacitus -Region us-central1 -Apply -StopCloudSql
```

Stopping Cloud SQL is reversible:

```powershell
gcloud sql instances patch praxisbytacitus-instance \
  --activation-policy=ALWAYS \
  --project=praxisbytacitus
```

## Artifact Registry Cleanup

The audit found that Docker image storage can grow quickly. Keep only the most
recent images needed for rollback.

```powershell
gcloud artifacts repositories list --project=praxisbytacitus
gcloud artifacts docker images list us-central1-docker.pkg.dev/praxisbytacitus/praxis --include-tags
gcloud artifacts docker images delete IMAGE_URL --delete-tags --quiet
```

Do not delete the image currently used by Cloud Run:

```powershell
gcloud run services describe praxis-backend --region=us-central1 --project=praxisbytacitus --format="value(spec.template.spec.containers[0].image)"
gcloud run services describe praxis-frontend --region=us-central1 --project=praxisbytacitus --format="value(spec.template.spec.containers[0].image)"
```
