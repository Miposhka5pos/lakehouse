
from datetime import datetime

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import (
    SparkSubmitOperator,
)


SPARK_JOBS_DIR = "/opt/airflow/spark/jobs/gold/retail"

SPARK_PACKAGES = (
    "com.crealytics:spark-excel_2.12:3.5.1_0.20.4,"
    "org.apache.hadoop:hadoop-aws:3.3.4,"
    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.8.1,"
    "org.apache.iceberg:iceberg-aws-bundle:1.8.1"
)


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
        deploy_mode="client",
        packages=SPARK_PACKAGES,
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
        deploy_mode="client",
        packages=SPARK_PACKAGES,
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
        deploy_mode="client",
        packages=SPARK_PACKAGES,
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
        deploy_mode="client",
        packages=SPARK_PACKAGES,
        verbose=True,
    )
