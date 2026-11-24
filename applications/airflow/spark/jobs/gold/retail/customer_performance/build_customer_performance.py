
from pyspark.sql import SparkSession


spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold-Customer-Performance")
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
        customer_id,
        COUNT(DISTINCT invoice) AS invoices_count,
        SUM(quantity) AS items_sold,
        SUM(quantity * price) AS revenue,
        ROUND(
            SUM(quantity * price) /
            NULLIF(COUNT(DISTINCT invoice), 0),
            2
        ) AS avg_invoice_value,
        MIN(invoice_date) AS first_purchase,
        MAX(invoice_date) AS last_purchase
    FROM demo.silver.online_retail_ii
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
""")

df_gold.writeTo(
    "demo.gold.customer_performance"
).using("iceberg").createOrReplace()

print("Gold rows:", df_gold.count())
print("Customer performance table loaded successfully")

spark.stop()
