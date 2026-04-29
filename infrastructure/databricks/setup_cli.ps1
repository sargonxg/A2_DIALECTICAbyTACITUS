param(
    [string]$Profile = "tacitus",
    [string]$WorkspaceHost = "",
    [string]$SecretScope = "tacitus",
    [switch]$SkipLogin,
    [switch]$SkipSecrets,
    [switch]$DeployBundle,
    [switch]$RunJob
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

    Write-Host "Databricks CLI not found. Installing with winget..."
    winget install --id Databricks.DatabricksCLI --exact --accept-package-agreements --accept-source-agreements

    if (Test-Path -LiteralPath $wingetPath) {
        return $wingetPath
    }

    throw "Databricks CLI install completed, but databricks.exe was not found. Restart PowerShell and retry."
}

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

function Put-Secret {
    param(
        [string]$Key,
        [string]$Prompt
    )

    $value = Read-SecretPlaintext $Prompt
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Secret $Key cannot be empty."
    }

    & $Dbx secrets put-secret $SecretScope $Key --profile $Profile --string-value $value
}

$Dbx = Get-DatabricksCli
Write-Host "Using Databricks CLI: $Dbx"
& $Dbx version

if (-not $SkipLogin) {
    if ([string]::IsNullOrWhiteSpace($WorkspaceHost)) {
        Write-Host "Starting Databricks OAuth login. Select your workspace in the browser."
        & $Dbx auth login $Profile
    }
    else {
        Write-Host "Starting Databricks OAuth login for $WorkspaceHost"
        & $Dbx auth login $Profile --host $WorkspaceHost
    }
}

Write-Host "Checking authenticated user..."
& $Dbx current-user me --profile $Profile

if (-not $SkipSecrets) {
    Write-Host "Creating secret scope '$SecretScope' if needed..."
    try {
        & $Dbx secrets create-scope $SecretScope --profile $Profile
    }
    catch {
        Write-Host "Secret scope may already exist. Continuing."
    }

    Put-Secret "neo4j-uri" "Neo4j URI"
    Put-Secret "neo4j-user" "Neo4j username"
    Put-Secret "neo4j-password" "Neo4j password"
    Put-Secret "neo4j-database" "Neo4j database"
    Put-Secret "gemini-api-key" "Gemini API key"

    Write-Host "Secrets now in scope '$SecretScope':"
    & $Dbx secrets list-secrets $SecretScope --profile $Profile
}

Write-Host "Validating Databricks bundle..."
& $Dbx bundle validate --profile $Profile

if ($DeployBundle) {
    Write-Host "Deploying Databricks bundle..."
    & $Dbx bundle deploy --profile $Profile
}

if ($RunJob) {
    Write-Host "Running tacitus_operational_loop..."
    & $Dbx bundle run tacitus_operational_loop --profile $Profile
}

Write-Host "Done."
