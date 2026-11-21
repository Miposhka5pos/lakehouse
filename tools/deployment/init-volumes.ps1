
$ErrorActionPreference = "Stop"

$Volumes = @(
    "lakehouse_minio_data",
    "lakehouse_postgres_data",
    "lakehouse_airflow_postgres_data"
)

foreach ($Volume in $Volumes) {
    $Existing = docker volume ls --format "{{.Name}}" |
        Where-Object { $_ -eq $Volume }

    if (-not $Existing) {
        Write-Host "Creating volume: $Volume"
        docker volume create $Volume | Out-Null

        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create volume: $Volume"
        }
    }
    else {
        Write-Host "Volume already exists: $Volume"
    }
}
