$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$DeploymentDir = Join-Path $ProjectRoot "platform\deployment"
$EnvFile = Join-Path $DeploymentDir ".env"
$LakehouseComposeFile = Join-Path $DeploymentDir "docker-compose.yml"
$HadoopComposeFile = Join-Path $DeploymentDir "hadoop-compose.yml"
function Get-LakehouseComposeArgs {
    if (-not (Test-Path $EnvFile)) { throw "Missing platform/deployment/.env. Copy .env.example and configure it." }
    if (-not (Test-Path $LakehouseComposeFile)) { throw "Docker Compose file not found: $LakehouseComposeFile" }
    return @("--env-file", $EnvFile, "-f", $LakehouseComposeFile)
}
function Get-HadoopComposeArgs {
    if (-not (Test-Path $HadoopComposeFile)) { throw "Docker Compose file not found: $HadoopComposeFile" }
    return @("-f", $HadoopComposeFile)
}
function Invoke-Compose {
    param([string[]]$ComposeArgs, [string[]]$Arguments, [string]$FailureMessage)
    & docker compose @ComposeArgs @Arguments
    if ($LASTEXITCODE -ne 0) { throw $FailureMessage }
}
