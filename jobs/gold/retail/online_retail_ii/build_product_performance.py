from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold")
    .getOrCreate()
)

df = spark.sql("""
    SELECT
        stock_code,
        COUNT(DISTINCT invoice) AS invoices_count,
        COUNT(DISTINCT customer_id) AS customers_count,
        SUM(quantity) AS items_sold,
        SUM(quantity * price) AS revenue
    FROM demo.silver.online_retail_ii
    GROUP BY stock_code;
""")

df.writeTo(
    "demo.gold.product_performance"
).using("iceberg").createOrReplace()

df.printSchema()
df.show(20, truncate=False)

print("Gold rows:", df.count())

print("Gold table loaded successfully")