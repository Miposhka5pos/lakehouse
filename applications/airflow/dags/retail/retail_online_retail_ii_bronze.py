
from datetime import datetime, timezone

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import (
    SparkSubmitOperator,
)


SPARK_APPLICATION = (
    "/opt/airflow/spark/jobs/bronze/retail/online_retail_ii/"
    "build_online_retail_ii.py"
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
        deploy_mode="cluster",

        packages=(
            "com.crealytics:spark-excel_2.12:3.5.1_0.20.4,"
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.2"
        ),

        conf={
            # YARN
            "spark.hadoop.yarn.resourcemanager.hostname": "resourcemanager",
            "spark.hadoop.yarn.resourcemanager.address": "resourcemanager:8032",
            "spark.yarn.submit.waitAppCompletion": "true",
            "spark.yarn.stagingDir": (
                "hdfs://namenode:9000/tmp/spark-staging"
            ),

            # Resource allocation
            "spark.executor.instances": "1",
            "spark.executor.cores": "1",
            "spark.executor.memory": "1g",
            "spark.driver.cores": "1",
            "spark.driver.memory": "1g",

            # HDFS
            "spark.hadoop.fs.defaultFS": "hdfs://namenode:9000",
            "spark.hadoop.dfs.client.use.datanode.hostname": "true",

            # Iceberg REST Catalog
            "spark.sql.extensions": (
                "org.apache.iceberg.spark.extensions."
                "IcebergSparkSessionExtensions"
            ),
            "spark.sql.catalog.demo": (
                "org.apache.iceberg.spark.SparkCatalog"
            ),
            "spark.sql.catalog.demo.type": "rest",
            "spark.sql.catalog.demo.uri": "http://rest:8181",
            "spark.sql.catalog.demo.io-impl": (
                "org.apache.iceberg.hadoop.HadoopFileIO"
            ),
            "spark.sql.catalog.demo.warehouse": (
                "hdfs://namenode:9000/warehouse"
            ),
            "spark.sql.defaultCatalog": "demo",

            # Spark event logs
            "spark.eventLog.enabled": "true",
            "spark.eventLog.dir": (
                "hdfs://namenode:9000/spark-events"
            ),
        },

        verbose=True,
    )
