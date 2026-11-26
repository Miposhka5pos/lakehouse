from datetime import datetime

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import (
    SparkSubmitOperator,
)


SPARK_JOBS_DIR = "/opt/airflow/spark/jobs/gold/retail"

SPARK_PACKAGES = (
    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.2"
)

SPARK_CONF = {
    "spark.yarn.stagingDir": "hdfs://namenode:9000/tmp/spark-staging",
}


default_args = {
    "retries": 0,
}


with DAG(
    dag_id="retail_online_retail_ii_gold",
    description="Build Gold data marts for Online Retail II",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    tags=["retail", "gold", "iceberg"],
) as dag:

    build_customer_performance = SparkSubmitOperator(
        task_id="build_customer_performance",
        application=(
            f"{SPARK_JOBS_DIR}/customer_performance/"
            "build_customer_performance.py"
        ),
        conn_id="spark_default",
        name="retail-online-retail-ii-gold-customer-performance",
        deploy_mode="cluster",
        packages=SPARK_PACKAGES,
        conf=SPARK_CONF,
        verbose=True,
    )

    build_monthly_sales = SparkSubmitOperator(
        task_id="build_monthly_sales",
        application=(
            f"{SPARK_JOBS_DIR}/monthly_sales_by_country/"
            "build_monthly_sales.py"
        ),
        conn_id="spark_default",
        name="retail-online-retail-ii-gold-monthly-sales",
        deploy_mode="cluster",
        packages=SPARK_PACKAGES,
        conf=SPARK_CONF,
        verbose=True,
    )

    build_product_performance = SparkSubmitOperator(
        task_id="build_product_performance",
        application=(
            f"{SPARK_JOBS_DIR}/product_performance/"
            "build_product_performance.py"
        ),
        conn_id="spark_default",
        name="retail-online-retail-ii-gold-product-performance",
        deploy_mode="cluster",
        packages=SPARK_PACKAGES,
        conf=SPARK_CONF,
        verbose=True,
    )

    build_product_sales = SparkSubmitOperator(
        task_id="build_product_sales",
        application=(
            f"{SPARK_JOBS_DIR}/product_sales/"
            "build_product_sales.py"
        ),
        conn_id="spark_default",
        name="retail-online-retail-ii-gold-product-sales",
        deploy_mode="cluster",
        packages=SPARK_PACKAGES,
        conf=SPARK_CONF,
        verbose=True,
    )

build_customer_performance >> build_monthly_sales
build_monthly_sales >> build_product_performance
build_product_performance >> build_product_sales