from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType


spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Silver")
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
        "org.apache.iceberg.hadoop.HadoopFileIO",
    )
    .config(
        "spark.sql.catalog.demo.warehouse",
        "hdfs://namenode:9000/warehouse",
    )
    .config("spark.sql.defaultCatalog", "demo")
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
    F.col("Customer_ID").cast("int").alias("customer_id"),
    F.trim(F.col("Country")).alias("country"),
    F.col("source_sheet"),
)

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

spark.stop()