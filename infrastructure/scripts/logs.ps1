
param(
    [Parameter(Position = 0)]
    [string]$Service
)

. "$PSScriptRoot\_common.ps1"

$ComposeArgs = Get-LakehouseComposeArgs

if ($Service) {
    docker compose @ComposeArgs logs -f $Service
}
else {
    docker compose @ComposeArgs logs -f
}
