
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

SOURCE_FILE = (
    "hdfs://namenode:9000/warehouse/landing/retail/"
    "online_retail_ii/source.xlsx"
)

TARGET_TABLE = "demo.bronze.online_retail_ii"

SHEETS = [
    "Year 2009-2010",
    "Year 2010-2011",
]

# Preserve original source values in the Bronze layer.
SOURCE_SCHEMA = StructType([
    StructField("Invoice", StringType(), True),
    StructField("StockCode", StringType(), True),
    StructField("Description", StringType(), True),
    StructField("Quantity", StringType(), True),
    StructField("InvoiceDate", StringType(), True),
    StructField("Price", StringType(), True),
    StructField("Customer ID", StringType(), True),
    StructField("Country", StringType(), True),
])


def read_excel_sheet(spark, sheet_name):
    logger.info("Reading Excel sheet: %s", sheet_name)

    df = (
        spark.read
        .format("com.crealytics.spark.excel")
        .option("dataAddress", f"'{sheet_name}'!A1")
        .option("header", "true")
        .option("maxRowsInMemory", "1000")
        .option("treatEmptyValuesAsNulls", "true")
        .option("usePlainNumberFormat", "true")
        .schema(SOURCE_SCHEMA)
        .load(SOURCE_FILE)
    )

    df = (
        df
        .withColumnRenamed("Customer ID", "Customer_ID")
        .withColumn("source_sheet", lit(sheet_name))
        .withColumn("source_file", lit(SOURCE_FILE))
        .withColumn("ingested_at", current_timestamp())
    )

    return df


def main():
    spark = (
        SparkSession.builder
        .appName("retail-online-retail-ii-bronze")
        .getOrCreate()
    )

    try:
        logger.info("Starting Online Retail II Bronze ingestion")
        logger.info("Source: %s", SOURCE_FILE)
        logger.info("Target: %s", TARGET_TABLE)

        # Create Bronze namespace if it does not exist.
        spark.sql("CREATE NAMESPACE IF NOT EXISTS demo.bronze")

        # Read both Excel sheets.
        dataframes = [
            read_excel_sheet(spark, sheet_name)
            for sheet_name in SHEETS
        ]

        # Combine both periods into one dataset.
        bronze_df = dataframes[0]

        for df in dataframes[1:]:
            bronze_df = bronze_df.unionByName(df)

        logger.info("Writing Bronze Iceberg table: %s", TARGET_TABLE)

        (
            bronze_df.writeTo(TARGET_TABLE)
            .using("iceberg")
            .tableProperty("format-version", "2")
            .createOrReplace()
        )

        logger.info("Bronze ingestion completed successfully")

    except Exception:
        logger.exception("Bronze ingestion failed")
        raise

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
