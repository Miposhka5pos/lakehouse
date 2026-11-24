from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType
import os

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Bronze")

    # Iceberg
    .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    .config(
        "spark.sql.catalog.demo",
        "org.apache.iceberg.spark.SparkCatalog",
    )
    .config("spark.sql.catalog.demo.type", "rest")
    .config("spark.sql.catalog.demo.uri", "http://rest:8181")
    .config(
        "spark.sql.catalog.demo.io-impl",
        "org.apache.iceberg.aws.s3.S3FileIO",
    )
    .config("spark.sql.catalog.demo.warehouse", "s3://warehouse/wh/")
    .config("spark.sql.catalog.demo.s3.endpoint", "http://minio:9000")
    .config("spark.sql.catalog.demo.s3.path-style-access", "true")
    .config("spark.sql.defaultCatalog", "demo")

    # MinIO / Hadoop S3A
    .config("spark.hadoop.fs.s3a.endpoint", os.environ["MINIO_ENDPOINT_URL"])
    .config("spark.hadoop.fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    )
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

    .getOrCreate()
)

df_bronze = spark.table("demo.bronze.online_retail_ii")

df_silver = df_bronze.select(
    F.trim(F.col("Invoice")).alias("invoice"),
    F.trim(F.col("StockCode")).alias("stock_code"),
    F.trim(F.col("Description")).alias("description"),
    F.col("Quantity").cast("int").alias("quantity"),
    F.to_timestamp(
        "InvoiceDate", "M/d/yy H:mm"
    ).alias("invoice_date"),
    F.col("Price").cast(DecimalType(10, 2)).alias("price"),
    F.col("Customer ID").cast("int").alias("customer_id"),
    F.trim(F.col("Country")).alias("country"),
    F.col("source_sheet"),
)

# Data quality statistics
quality_metrics = df_silver.select(
    F.count("*").alias("total_rows"),
    F.count(
        F.when(F.col("invoice_date").isNull(), 1)
    ).alias("null_invoice_date"),
    F.count(
        F.when(F.col("quantity").isNull(), 1)
    ).alias("null_quantity"),
    F.count(
        F.when(F.col("price").isNull(), 1)
    ).alias("null_price"),
    F.count(
        F.when(F.col("customer_id").isNull(), 1)
    ).alias("null_customer_id"),
)

print("Silver data quality metrics:")
quality_metrics.show(truncate=False)

df_silver.writeTo(
    "demo.silver.online_retail_ii"
).using("iceberg").createOrReplace()

print("Silver table loaded successfully")