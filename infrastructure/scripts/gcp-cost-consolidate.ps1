param(
  [string]$ProjectId = $(gcloud config get-value project 2>$null),
  [string]$Region = "us-central1",
  [switch]$Apply,
  [switch]$PauseSchedulers,
  [switch]$StopCloudSql
)

$ErrorActionPreference = "Stop"

if (-not $ProjectId) {
  throw "No GCP project configured. Run: gcloud config set project PROJECT_ID"
}

function Invoke-Plan {
  param([string]$Command)
  if ($Apply) {
    Write-Host "RUN $Command"
    Invoke-Expression $Command
  } else {
    Write-Host "DRY $Command"
  }
}

Write-Host "==> Cost consolidation plan for $ProjectId / $Region"
Write-Host "    Apply=$Apply PauseSchedulers=$PauseSchedulers StopCloudSql=$StopCloudSql"

$services = gcloud run services list --platform=managed --project=$ProjectId --format="value(metadata.name,region)"
foreach ($line in $services) {
  if (-not $line.Trim()) { continue }
  $parts = $line -split "\s+"
  $name = $parts[0]
  $serviceRegion = if ($parts.Length -gt 1 -and $parts[1]) { $parts[1] } else { $Region }
  Invoke-Plan "gcloud run services update $name --region=$serviceRegion --project=$ProjectId --min-instances=0 --max-instances=1 --cpu-throttling --no-cpu-boost --quiet"
}

if ($PauseSchedulers) {
  $jobs = gcloud scheduler jobs list --location=$Region --project=$ProjectId --format="value(name.basename())"
  foreach ($job in $jobs) {
    if (-not $job.Trim()) { continue }
    Invoke-Plan "gcloud scheduler jobs pause $job --location=$Region --project=$ProjectId --quiet"
  }
}

if ($StopCloudSql) {
  $instances = gcloud sql instances list --project=$ProjectId --format="value(name)"
  foreach ($instance in $instances) {
    if (-not $instance.Trim()) { continue }
    Invoke-Plan "gcloud sql instances patch $instance --activation-policy=NEVER --project=$ProjectId --quiet"
  }
}

Write-Host "`nArtifact Registry cleanup is intentionally not automatic. Delete old images only after confirming rollback requirements:"
Write-Host "gcloud artifacts docker images list $Region-docker.pkg.dev/$ProjectId/REPOSITORY --include-tags"
Write-Host "gcloud artifacts docker images delete IMAGE_URL --delete-tags --quiet"
