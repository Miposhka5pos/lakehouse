param([ValidateSet("all", "lakehouse", "hadoop")][string]$Stack = "all")
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
# Stop services only; persistent volumes are intentionally preserved.
if ($Stack -in @("all", "hadoop")) {
    $composeArgs = Get-HadoopComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("down") -FailureMessage "Failed to stop Hadoop."
}
if ($Stack -in @("all", "lakehouse")) {
    $composeArgs = Get-LakehouseComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("down") -FailureMessage "Failed to stop Lakehouse."
}
