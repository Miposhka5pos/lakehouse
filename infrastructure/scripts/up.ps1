
. "$PSScriptRoot\_common.ps1"

$ComposeArgs = Get-LakehouseComposeArgs

docker compose @ComposeArgs up -d

if ($LASTEXITCODE -ne 0) {
    throw "Failed to start Lakehouse."
}
