from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Bronze")
    .getOrCreate()
)

jvm = spark.sparkContext._jvm
jvm.org.apache.poi.util.IOUtils.setByteArrayMaxOverride(200_000_000)

source_path = "s3a://warehouse/landing/retail/online_retail_ii/source.xlsx"

df_2009 = (
    spark.read
    .format("excel")
    .option("header", "true")
    .option("inferSchema", "false")
    .option("maxRowsInMemory", 1000)
    .option("dataAddress", "'Year 2009-2010'!A1")
    .load(source_path)
    .withColumn("source_sheet", lit("Year 2009-2010"))
)

df_2010 = (
    spark.read
    .format("excel")
    .option("header", "true")
    .option("inferSchema", "false")
    .option("maxRowsInMemory", 1000)
    .option("dataAddress", "'Year 2010-2011'!A1")
    .load(source_path)
    .withColumn("source_sheet", lit("Year 2010-2011"))
)

df_bronze = df_2009.unionByName(df_2010)

df_bronze.writeTo(
    "demo.bronze.online_retail_ii"
).using("iceberg").createOrReplace()

print("Bronze table loaded successfully")