from datetime import datetime

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import (
    SparkSubmitOperator,
)

SPARK_APPLICATION = (
    "/opt/airflow/spark/jobs/silver/retail/online_retail_ii/build_online_retail_ii.py"
)

with DAG(
    dag_id="retail_online_retail_ii_silver",
    description="Build Silver Iceberg table for Online Retail II",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "retries": 0,
    },
    tags=["retail", "silver", "iceberg"],
) as dag:

    build_silver = SparkSubmitOperator(
        task_id="build_silver",
        application=SPARK_APPLICATION,
        conn_id="spark_default",
        name="retail-online-retail-ii-silver",
        deploy_mode="cluster",
        packages=(
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.2"
        ),
        conf={
            "spark.yarn.stagingDir": "hdfs://namenode:9000/tmp/spark-staging",
        },
        verbose=True,
    )
