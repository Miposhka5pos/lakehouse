
from datetime import datetime, timedelta, timezone
import logging
import os
import tempfile
import uuid

import requests

from airflow import DAG
from airflow.operators.python import PythonOperator


SOURCE_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00502/online_retail_II.xlsx"
)

HDFS_WEBHDFS_URL = "http://namenode:9870/webhdfs/v1"
HDFS_USER = "hadoop"

HDFS_DIRECTORY = "/warehouse/landing/retail/online_retail_ii"
HDFS_FILE = f"{HDFS_DIRECTORY}/source.xlsx"

CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

def hdfs_request(method: str, path: str, **kwargs) -> requests.Response:
    """Execute a WebHDFS request against the NameNode."""
    url = f"{HDFS_WEBHDFS_URL}{path}"

    params = kwargs.pop("params", {})
    params["user.name"] = HDFS_USER

    timeout = kwargs.pop("timeout", (15, 120))

    response = requests.request(
        method,
        url,
        params=params,
        timeout=timeout,
        **kwargs,
    )
    response.raise_for_status()
    return response

def download_and_upload_source() -> None:
    """Download the source XLSX and upload it to the HDFS landing zone."""

    logging.info("Creating HDFS directory: %s", HDFS_DIRECTORY)

    mkdir_response = hdfs_request(
        "PUT",
        HDFS_DIRECTORY,
        params={"op": "MKDIRS"},
    )

    if not mkdir_response.json().get("boolean"):
        raise RuntimeError(
            f"Failed to create HDFS directory: {HDFS_DIRECTORY}"
        )

    temporary_hdfs_file = (
        f"{HDFS_DIRECTORY}/.source-{uuid.uuid4().hex}.tmp"
    )

    logging.info("Downloading source file from %s", SOURCE_URL)

    file_size = 0

    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as local_file:
            with requests.get(
                SOURCE_URL,
                stream=True,
                timeout=(15, 300),
            ) as response:
                response.raise_for_status()

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        local_file.write(chunk)
                        file_size += len(chunk)

            if file_size == 0:
                raise RuntimeError("Downloaded source file is empty")

            local_file.seek(0)

            logging.info(
                "Uploading %.2f MiB to HDFS: %s",
                file_size / (1024 * 1024),
                temporary_hdfs_file,
            )

            upload_response = hdfs_request(
                "PUT",
                temporary_hdfs_file,
                params={
                    "op": "CREATE",
                    "overwrite": "true",
                },
                data=local_file,
                headers={"Content-Type": CONTENT_TYPE},
                timeout=(15, 300),
            )

            if upload_response.status_code != 201:
                raise RuntimeError(
                    "Unexpected WebHDFS CREATE status: "
                    f"{upload_response.status_code}"
                )

        # Replace the previous source only after the new file
        # has been completely uploaded.
        logging.info("Replacing HDFS source file: %s", HDFS_FILE)

        delete_response = hdfs_request(
            "DELETE",
            HDFS_FILE,
            params={"op": "DELETE"},
        )

        if delete_response.status_code == 200:
            logging.info("Previous HDFS source file deleted")
        elif delete_response.status_code != 404:
            raise RuntimeError(
                f"Unexpected HDFS DELETE status: "
                f"{delete_response.status_code}"
            )

        rename_response = hdfs_request(
            "PUT",
            temporary_hdfs_file,
            params={
                "op": "RENAME",
                "destination": HDFS_FILE,
            },
        )

        if not rename_response.json().get("boolean"):
            raise RuntimeError(
                f"Failed to rename temporary HDFS file "
                f"to {HDFS_FILE}"
            )

        logging.info(
            "Source file uploaded successfully: hdfs://namenode:9000%s",
            HDFS_FILE,
        )

    except Exception:
        logging.exception("Failed to upload source file to HDFS")

        # Remove incomplete temporary file if it exists.
        try:
            hdfs_request(
                "DELETE",
                temporary_hdfs_file,
                params={"op": "DELETE"},
            )
        except requests.RequestException:
            logging.warning(
                "Could not clean up temporary HDFS file: %s",
                temporary_hdfs_file,
            )

        raise


with DAG(
    dag_id="retail_online_retail_ii_landing",
    description="Download Online Retail II XLSX and store it in HDFS landing",
    start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 0,
    },
    tags=["retail", "online_retail_ii", "landing", "hdfs"],
) as dag:

    upload_source = PythonOperator(
        task_id="download_and_upload_source",
        python_callable=download_and_upload_source,
        execution_timeout=timedelta(minutes=15),
    )
