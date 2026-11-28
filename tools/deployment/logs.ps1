param(
    [Parameter(Position = 0)][string]$Service,
    [ValidateSet("all", "lakehouse", "hadoop")][string]$Stack = "all",
    [switch]$Tail
)
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
$logArgs = @("logs", "-f")
if ($Tail) { $logArgs += @("--tail", "200") }
if ($Service) { $logArgs += $Service }
if ($Stack -eq "all") { throw "Choose -Stack lakehouse or -Stack hadoop when following logs." }
if ($Stack -eq "lakehouse") {
    $composeArgs = Get-LakehouseComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments $logArgs -FailureMessage "Failed to read Lakehouse logs."
}
else {
    $composeArgs = Get-HadoopComposeArgs
    Invoke-Compose -ComposeArgs $composeArgs -Arguments $logArgs -FailureMessage "Failed to read Hadoop logs."
}
