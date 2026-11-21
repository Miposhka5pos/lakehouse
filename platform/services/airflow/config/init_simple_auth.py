import json
import os
from pathlib import Path

username = os.environ.get("AIRFLOW_AUTH_USERNAME")
password = os.environ.get("AIRFLOW_AUTH_PASSWORD")

if not username or not password:
    raise RuntimeError("Airflow authentication credentials are not configured")

if any(char in username for char in (":", ",")):
    raise RuntimeError("AIRFLOW_AUTH_USERNAME contains an invalid character")

password_file = Path(
    "/opt/airflow/config/simple_auth_manager_passwords.json"
)

password_file.parent.mkdir(parents=True, exist_ok=True)

temporary_file = password_file.with_suffix(".json.tmp")
temporary_file.write_text(
    json.dumps({username: password}) + "\n",
    encoding="utf-8",
)

os.replace(temporary_file, password_file)

try:
    os.chmod(password_file, 0o600)
except OSError:
    pass

print("Airflow SimpleAuthManager credentials initialized.")
