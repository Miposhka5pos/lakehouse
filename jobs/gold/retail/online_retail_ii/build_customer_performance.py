from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Gold-Customers")
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