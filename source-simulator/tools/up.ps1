$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"
$composeArgs = Get-SourceSimulatorComposeArgs
$network = docker network ls --format "{{.Name}}" | Where-Object { $_ -eq "lakehouse_iceberg_net" }
if (-not $network) { throw "Docker network lakehouse_iceberg_net does not exist. Start Lakehouse first with tools/deployment/up.ps1." }
Invoke-SourceSimulatorCompose -ComposeArgs $composeArgs -Arguments @("config", "--quiet") -FailureMessage "Invalid Source Simulator Compose configuration."
# Starts PostgreSQL only. No generator image build, seed, or data mutations are run.
Invoke-SourceSimulatorCompose -ComposeArgs $composeArgs -Arguments @("up", "-d", "source-postgres") -FailureMessage "Failed to start Source Simulator PostgreSQL."
Invoke-SourceSimulatorCompose -ComposeArgs $composeArgs -Arguments @("ps", "source-postgres") -FailureMessage "Failed to get Source Simulator PostgreSQL status."
