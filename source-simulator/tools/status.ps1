$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
$composeArgs = Get-SourceSimulatorComposeArgs
Invoke-SourceSimulatorCompose -ComposeArgs $composeArgs -Arguments @("ps", "-a", "source-postgres") -FailureMessage "Failed to get Source Simulator PostgreSQL status."
