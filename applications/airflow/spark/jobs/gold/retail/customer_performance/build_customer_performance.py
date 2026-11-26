from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold-Customer-Performance")
    .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    .config("spark.sql.catalog.demo", "org.apache.iceberg.spark.SparkCatalog")
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

spark.sql("CREATE NAMESPACE IF NOT EXISTS demo.gold")

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