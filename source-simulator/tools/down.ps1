$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
$composeArgs = Get-SourceSimulatorComposeArgs
Invoke-SourceSimulatorCompose -ComposeArgs $composeArgs -Arguments @("stop", "source-postgres") -FailureMessage "Failed to stop Source Simulator PostgreSQL."
