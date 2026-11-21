
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectRoot "infrastructure\.env"
$ComposeFile = Join-Path $ProjectRoot "infrastructure\docker-compose.yml"

function Get-LakehouseComposeArgs {
    if (-not (Test-Path $EnvFile)) {
        throw "Missing infrastructure/.env. Copy .env.example and configure it."
    }

    if (-not (Test-Path $ComposeFile)) {
        throw "Docker Compose file not found: $ComposeFile"
    }

    return @(
        "--env-file", $EnvFile,
        "-f", $ComposeFile
    )
}
