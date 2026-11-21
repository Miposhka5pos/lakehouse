from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Silver")
    .getOrCreate()
)

jvm = spark.sparkContext._jvm
# jvm.org.apache.poi.util.IOUtils.setByteArrayMaxOverride(200_000_000)

df = spark.table("demo.bronze.online_retail_ii")

df = df.select(
    F.trim(F.col("Invoice")).alias("invoice"),
    F.trim(F.col("StockCode")).alias("stock_code"),
    F.trim(F.col("Description")).alias("description"),
    F.col("Quantity").cast("int").alias("quantity"),
    F.to_timestamp("InvoiceDate", "M/d/yy H:mm").alias("invoice_date"),
    F.col("Price").cast(DecimalType(10, 2)).alias("price"),
    F.col("Customer ID").cast("int").alias("customer_id"),
    F.trim(F.col("Country")).alias("country"),
    F.col("source_sheet")
)

df.writeTo(
    "demo.silver.online_retail_ii"
).using("iceberg").createOrReplace()

print("Silver table loaded successfully")