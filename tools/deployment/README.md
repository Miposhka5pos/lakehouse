# Deployment tools

PowerShell deployment helpers for the Lakehouse stacks.

Run from the repository root:

```powershell
.\\tools\\deployment\\up.ps1                 # Lakehouse + Hadoop
.\\tools\\deployment\\up.ps1 -Stack lakehouse
.\\tools\\deployment\\up.ps1 -Stack hadoop
.\\tools\\deployment\\status.ps1
.\\tools\\deployment\\logs.ps1 -Stack lakehouse
.\\tools\\deployment\\logs.ps1 -Stack hadoop
.\\tools\\deployment\\down.ps1                # stop both stacks
```

The Lakehouse stack includes its Airflow services through Compose `include`. Hadoop is managed separately through `platform/deployment/hadoop-compose.yml`.

The scripts validate Compose configuration before starting services and initialize named volumes if missing. The down script stops/removes containers and project networks only; it does not use `down -v` and never deletes persistent volumes.
