
. "$PSScriptRoot\_common.ps1"

$ComposeArgs = Get-LakehouseComposeArgs

docker compose @ComposeArgs ps

if ($LASTEXITCODE -ne 0) {
    throw "Failed to get Lakehouse status."
}
