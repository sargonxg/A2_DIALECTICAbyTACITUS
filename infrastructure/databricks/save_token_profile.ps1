param(
    [string]$Profile = "tacitus",
    [string]$WorkspaceHost = ""
)

$ErrorActionPreference = "Stop"

function Read-SecretPlaintext {
    param([string]$Prompt)

    $secure = Read-Host $Prompt -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

function Get-DatabricksCli {
    $cmd = Get-Command databricks -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $wingetPath = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\Databricks.DatabricksCLI_Microsoft.Winget.Source_8wekyb3d8bbwe\databricks.exe"
    if (Test-Path -LiteralPath $wingetPath) {
        return $wingetPath
    }

    throw "Databricks CLI not found. Run infrastructure\databricks\setup_cli.ps1 first."
}

if ([string]::IsNullOrWhiteSpace($WorkspaceHost)) {
    $WorkspaceHost = Read-Host "Databricks workspace host, for example https://dbc-xxxx.cloud.databricks.com"
}

if ($WorkspaceHost -notmatch '^https://') {
    throw "WorkspaceHost must start with https://"
}

$token = Read-SecretPlaintext "Databricks access token"
if ([string]::IsNullOrWhiteSpace($token)) {
    throw "Token cannot be empty."
}

$configPath = Join-Path $HOME ".databrickscfg"
if (Test-Path -LiteralPath $configPath) {
    $existing = Get-Content -Raw -LiteralPath $configPath
}
else {
    $existing = ""
}

$profileBlock = @"
[$Profile]
host = $WorkspaceHost
token = $token

"@

$pattern = "(?ms)^\[$([regex]::Escape($Profile))\]\s+.*?(?=^\[|\z)"
if ($existing -match $pattern) {
    $updated = [regex]::Replace($existing, $pattern, $profileBlock)
}
else {
    $updated = $existing.TrimEnd() + "`r`n" + $profileBlock
}

Set-Content -LiteralPath $configPath -Value $updated -Encoding UTF8

$Dbx = Get-DatabricksCli
Write-Host "Saved Databricks profile '$Profile' to $configPath"
Write-Host "Validating token with current-user endpoint..."
& $Dbx current-user me --profile $Profile

Write-Host "Token saved. Rotate this token later because the original value was pasted into chat."
