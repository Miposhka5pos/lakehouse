
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$EnvFile = Join-Path $ProjectRoot "platform\deployment\.env"
$ComposeFile = Join-Path $ProjectRoot "platform\deployment\docker-compose.yml"

function Get-LakehouseComposeArgs {
    if (-not (Test-Path $EnvFile)) {
        throw "Missing platform/deployment/.env. Copy .env.example and configure it."
    }

    if (-not (Test-Path $ComposeFile)) {
        throw "Docker Compose file not found: $ComposeFile"
    }

    return @(
        "--env-file", $EnvFile,
        "-f", $ComposeFile
    )
}
