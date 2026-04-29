param(
    [string]$Profile = "tacitus",
    [string]$AccountProfile = "",
    [string]$StartMonth = (Get-Date -Format "yyyy-MM"),
    [string]$EndMonth = (Get-Date -Format "yyyy-MM"),
    [string]$OutputPath = "databricks_billable_usage.csv"
)

$ErrorActionPreference = "Stop"

function Get-DatabricksCli {
    $cmd = Get-Command databricks -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $wingetPath = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\Databricks.DatabricksCLI_Microsoft.Winget.Source_8wekyb3d8bbwe\databricks.exe"
    if (Test-Path -LiteralPath $wingetPath) {
        return $wingetPath
    }

    throw "Databricks CLI not found."
}

$Dbx = Get-DatabricksCli

Write-Host "Workspace identity for profile '$Profile':"
& $Dbx current-user me --profile $Profile

Write-Host ""
Write-Host "Workspace jobs tagged project=tacitus-dialectica:"
& $Dbx jobs list --profile $Profile -o json | Out-String

if (-not [string]::IsNullOrWhiteSpace($AccountProfile)) {
    Write-Host ""
    Write-Host "Downloading account billable usage from $StartMonth to $EndMonth."
    Write-Host "This requires account-level permissions."
    & $Dbx account billable-usage download $StartMonth $EndMonth --profile $AccountProfile | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Host "Wrote $OutputPath"
}
else {
    Write-Host ""
    Write-Host "Skipping account billable usage download."
    Write-Host "To check spend/credits from CLI, configure an account-level profile, then run:"
    Write-Host ".\infrastructure\databricks\check_usage.ps1 -Profile tacitus -AccountProfile <account-profile>"
}

Write-Host ""
Write-Host "Important: Databricks budgets are alerts, not hard spending stops. For a hard cap, configure the cloud billing account budget/quota too."
