from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
import os

spark = (
    SparkSession.builder
    .appName("OnlineRetailII-Bronze")

    # Iceberg
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

    # MinIO / Hadoop S3A
    .config("spark.hadoop.fs.s3a.endpoint", os.environ["MINIO_ENDPOINT_URL"])
    .config("spark.hadoop.fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    )
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

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