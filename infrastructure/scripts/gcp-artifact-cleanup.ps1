param(
  [string]$ProjectId = $(gcloud config get-value project 2>$null),
  [string]$Region = "us-central1",
  [string]$Repository = "praxis",
  [int]$KeepPerPackage = 3,
  [switch]$Apply
)

$ErrorActionPreference = "Stop"

if (-not $ProjectId) {
  throw "No GCP project configured. Run: gcloud config set project PROJECT_ID"
}

$repoUrl = "$Region-docker.pkg.dev/$ProjectId/$Repository"
$images = gcloud artifacts docker images list $repoUrl --include-tags --format=json | ConvertFrom-Json

$protected = New-Object 'System.Collections.Generic.HashSet[string]'
$services = gcloud run services list --platform=managed --project=$ProjectId --format=json | ConvertFrom-Json
foreach ($service in $services) {
  $serviceRegion = $service.metadata.labels.'cloud.googleapis.com/location'
  if (-not $serviceRegion) { continue }
  $revision = $service.status.latestReadyRevisionName
  if (-not $revision) { continue }
  $revisionJson = gcloud run revisions describe $revision --region=$serviceRegion --project=$ProjectId --format=json | ConvertFrom-Json
  $digest = $revisionJson.status.imageDigest
  if ($digest -and $digest.StartsWith($repoUrl)) {
    [void]$protected.Add($digest)
  }
}

$delete = @()
foreach ($group in ($images | Group-Object package)) {
  $sorted = $group.Group | Sort-Object createTime -Descending
  $keep = $sorted | Select-Object -First $KeepPerPackage
  $keepDigests = New-Object 'System.Collections.Generic.HashSet[string]'
  foreach ($item in $keep) {
    [void]$keepDigests.Add("$($item.package)@$($item.version)")
  }

  foreach ($item in $sorted) {
    $url = "$($item.package)@$($item.version)"
    $hasTag = $item.tags -and $item.tags.Count -gt 0
    if ($hasTag -or $protected.Contains($url) -or $keepDigests.Contains($url)) {
      continue
    }
    $delete += $url
  }
}

Write-Host "Repository: $repoUrl"
Write-Host "Images found: $($images.Count)"
Write-Host "Protected current Cloud Run digests: $($protected.Count)"
Write-Host "Delete candidates: $($delete.Count)"

foreach ($url in $delete) {
  if ($Apply) {
    Write-Host "DELETE $url"
    gcloud artifacts docker images delete $url --delete-tags --quiet
  } else {
    Write-Host "DRY $url"
  }
}
