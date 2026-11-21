
. "$PSScriptRoot\_common.ps1"

$ComposeArgs = Get-LakehouseComposeArgs

docker compose @ComposeArgs down

if ($LASTEXITCODE -ne 0) {
    throw "Failed to stop Lakehouse."
}
