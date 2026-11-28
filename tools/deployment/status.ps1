param([ValidateSet("all", "lakehouse", "hadoop")][string]$Stack = "all")
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
if ($Stack -in @("all", "lakehouse")) {
    Write-Host "=== Lakehouse ===" -ForegroundColor Cyan
    $composeArgs = Get-LakehouseComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("ps", "-a") -FailureMessage "Failed to get Lakehouse status."
}
if ($Stack -in @("all", "hadoop")) {
    Write-Host "=== Hadoop ===" -ForegroundColor Cyan
    $composeArgs = Get-HadoopComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("ps", "-a") -FailureMessage "Failed to get Hadoop status."
}
