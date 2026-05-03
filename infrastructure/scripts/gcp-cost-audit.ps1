param(
  [string]$ProjectId = $(gcloud config get-value project 2>$null),
  [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

if (-not $ProjectId) {
  throw "No GCP project configured. Run: gcloud config set project PROJECT_ID"
}

Write-Host "==> Cost audit for project $ProjectId / region $Region"

Write-Host "`n==> Cloud Run services"
gcloud run services list --platform=managed --project=$ProjectId --format="table(metadata.name,region,status.url)"

Write-Host "`n==> Cloud Scheduler jobs"
gcloud scheduler jobs list --location=$Region --project=$ProjectId --format="table(name.basename(),state,schedule,httpTarget.uri)"

Write-Host "`n==> Cloud SQL instances"
gcloud sql instances list --project=$ProjectId --format="table(name,region,state,settings.activationPolicy,settings.tier,settings.dataDiskSizeGb)"

Write-Host "`n==> Spanner instances"
gcloud spanner instances list --project=$ProjectId --format="table(name,config,processingUnits,nodeCount,state)" 2>$null

Write-Host "`n==> Redis instances"
gcloud redis instances list --region=$Region --project=$ProjectId --format="table(name,tier,memorySizeGb,state)" 2>$null

Write-Host "`n==> Artifact Registry repositories"
gcloud artifacts repositories list --project=$ProjectId --format="table(name.basename(),location,format,sizeBytes)"

Write-Host "`n==> Compute instances/disks/addresses"
gcloud compute instances list --project=$ProjectId --format="table(name,zone,status,machineType.basename())" 2>$null
gcloud compute disks list --project=$ProjectId --format="table(name,zone,sizeGb,type.basename(),users)" 2>$null
gcloud compute addresses list --project=$ProjectId --format="table(name,region,addressType,status,purpose,address)" 2>$null

Write-Host "`n==> Vertex AI endpoints/index endpoints"
gcloud ai endpoints list --region=$Region --project=$ProjectId --format="table(name,displayName)" 2>$null
gcloud ai index-endpoints list --region=$Region --project=$ProjectId --format="table(name,displayName,deployedIndexes)" 2>$null

Write-Host "`nReview likely idle-cost sources first: Cloud SQL activationPolicy=ALWAYS, Spanner instances, Redis, Compute disks/addresses, Vertex endpoints, and large Artifact Registry repositories."
