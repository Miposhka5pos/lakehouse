$ErrorActionPreference = "Stop"
$SourceSimulatorRoot = Split-Path -Parent $PSScriptRoot
$DeploymentDir = Join-Path $SourceSimulatorRoot "deployment"
$EnvFile = Join-Path $DeploymentDir ".env"
$ComposeFile = Join-Path $DeploymentDir "docker-compose.yml"
function Get-SourceSimulatorComposeArgs {
    if (-not (Test-Path $EnvFile)) { throw "Missing source-simulator/deployment/.env. Copy .env.example to .env and set POSTGRES_PASSWORD." }
    if (-not (Test-Path $ComposeFile)) { throw "Docker Compose file not found: $ComposeFile" }
    return @("--env-file", $EnvFile, "-f", $ComposeFile)
}
function Invoke-SourceSimulatorCompose {
    param([string[]]$ComposeArgs, [string[]]$Arguments, [string]$FailureMessage)
    & docker compose @ComposeArgs @Arguments
    if ($LASTEXITCODE -ne 0) { throw $FailureMessage }
}
