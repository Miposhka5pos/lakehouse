from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold")
    .getOrCreate()
)

df = spark.sql("""
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

df.writeTo(
    "demo.gold.monthly_sales_by_country"
).using("iceberg").createOrReplace()

df.printSchema()
df.show(20, truncate=False)

print("Gold rows:", df.count())

print("Gold table loaded successfully")