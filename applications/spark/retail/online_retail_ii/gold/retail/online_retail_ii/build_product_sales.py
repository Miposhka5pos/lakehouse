
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold-Products")
    .getOrCreate()
)

df = spark.sql("""
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

df.writeTo(
    "demo.gold.product_sales"
).using("iceberg").createOrReplace()

df.show(20, truncate=False)

print("Gold rows:", df.count())

print("Gold table loaded successfully")
