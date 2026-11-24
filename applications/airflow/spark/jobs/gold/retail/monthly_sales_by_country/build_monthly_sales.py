
from pyspark.sql import SparkSession


spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold-Monthly-Sales")
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
    .getOrCreate()
)

df_gold = spark.sql("""
    SELECT
        DATE_TRUNC('MONTH', invoice_date) AS sales_month,
        country,
        COUNT(DISTINCT invoice) AS invoices_count,
        COUNT(DISTINCT customer_id) AS customers_count,
        SUM(quantity) AS items_sold,
        SUM(quantity * price) AS revenue
    FROM demo.silver.online_retail_ii
    GROUP BY
        DATE_TRUNC('MONTH', invoice_date),
        country
""")

df_gold.writeTo(
    "demo.gold.monthly_sales_by_country"
).using("iceberg").createOrReplace()

print("Gold rows:", df_gold.count())
print("Monthly sales by country table loaded successfully")

spark.stop()
