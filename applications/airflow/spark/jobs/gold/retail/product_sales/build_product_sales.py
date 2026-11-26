from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold-Product-Sales")
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
        stock_code,
        description,
        COUNT(DISTINCT invoice) AS invoices_count,
        COUNT(DISTINCT customer_id) AS customers_count,
        SUM(quantity) AS items_sold,
        SUM(quantity * price) AS revenue,
        ROUND(
            SUM(quantity * price) / NULLIF(SUM(quantity), 0),
            2
        ) AS avg_unit_price
    FROM demo.silver.online_retail_ii
    GROUP BY stock_code, description
""")

df_gold.writeTo(
    "demo.gold.product_sales"
).using("iceberg").createOrReplace()

print("Gold rows:", df_gold.count())
print("Product sales table loaded successfully")

spark.stop()