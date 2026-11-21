
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\_common.ps1"

# Prepare persistent Docker volumes.
& "$PSScriptRoot\init-volumes.ps1"

# Build Compose arguments.
$ComposeArgs = Get-LakehouseComposeArgs

# Validate Compose configuration before starting services.
docker compose @ComposeArgs config --quiet

if ($LASTEXITCODE -ne 0) {
    throw "Invalid Docker Compose configuration."
}

# Start services.
docker compose @ComposeArgs up -d

if ($LASTEXITCODE -ne 0) {
    throw "Failed to start Lakehouse."
}
