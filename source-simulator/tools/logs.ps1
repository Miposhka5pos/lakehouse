param([int]$Tail = 200)
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
$composeArgs = Get-SourceSimulatorComposeArgs
Invoke-SourceSimulatorCompose -ComposeArgs $composeArgs -Arguments @("logs", "-f", "--tail", "$Tail", "source-postgres") -FailureMessage "Failed to read Source Simulator PostgreSQL logs."
