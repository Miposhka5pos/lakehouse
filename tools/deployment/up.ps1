param([ValidateSet("all", "lakehouse", "hadoop")][string]$Stack = "all")
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
if ($Stack -in @("all", "lakehouse")) {
    & "$PSScriptRoot\init-volumes.ps1"
    $composeArgs = Get-LakehouseComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("config", "--quiet") -FailureMessage "Invalid Lakehouse Compose configuration."
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("up", "-d", "--build") -FailureMessage "Failed to start Lakehouse."
}
if ($Stack -in @("all", "hadoop")) {
    $composeArgs = Get-HadoopComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("config", "--quiet") -FailureMessage "Invalid Hadoop Compose configuration."
    Invoke-Compose -ComposeArgs $composeArgs -Arguments @("up", "-d", "--build") -FailureMessage "Failed to start Hadoop."
}
