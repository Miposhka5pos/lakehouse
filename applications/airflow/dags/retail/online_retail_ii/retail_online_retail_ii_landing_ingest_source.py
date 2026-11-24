from datetime import datetime, timedelta, timezone
import logging
import os

import boto3
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator


SOURCE_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00502/online_retail_II.xlsx"
)
S3_BUCKET = "warehouse"
S3_KEY = "landing/retail/online_retail_ii/source.xlsx"
CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


def download_and_upload_source() -> None:
    """Download the source XLSX and upload it to the MinIO landing zone."""
    endpoint_url = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")

    logging.info("Downloading source file from %s", SOURCE_URL)
    response = requests.get(SOURCE_URL, timeout=(15, 300))
    response.raise_for_status()

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    file_size = len(response.content)
    logging.info(
        "Uploading %.2f MiB to s3://%s/%s",
        file_size / (1024 * 1024),
        S3_BUCKET,
        S3_KEY,
    )

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=response.content,
        ContentType=CONTENT_TYPE,
    )

    logging.info(
        "Source file uploaded successfully: s3://%s/%s",
        S3_BUCKET,
        S3_KEY,
    )


with DAG(
    dag_id="retail_online_retail_ii_landing_ingest_source",
    description="Download Online Retail II XLSX and store it in MinIO landing",
    start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["retail", "online_retail_ii", "landing", "ingestion"],
) as dag:
    upload_source = PythonOperator(
        task_id="download_and_upload_source",
        python_callable=download_and_upload_source,
        execution_timeout=timedelta(minutes=15),
    )
