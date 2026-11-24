
from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import (
    SparkSubmitOperator,
)

SPARK_APPLICATION = (
    "/opt/airflow/spark/jobs/bronze/retail/online_retail_ii/build_online_retail_ii.py"
)

with DAG(
    dag_id="retail_online_retail_ii_bronze",
    description="Load Online Retail II data into Bronze Iceberg table",
    start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 0,
    },
    tags=["retail", "online_retail_ii", "bronze", "spark"],
) as dag:

    build_bronze = SparkSubmitOperator(
        task_id="build_bronze",
        application=SPARK_APPLICATION,
        conn_id="spark_default",
        name="retail-online-retail-ii-bronze",
        deploy_mode="client",
        packages=(
            "com.crealytics:spark-excel_2.12:3.5.1_0.20.4,"
            "org.apache.hadoop:hadoop-aws:3.3.4,"
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.8.1,"
            "org.apache.iceberg:iceberg-aws-bundle:1.8.1"
        ),
        verbose=True,
    )
