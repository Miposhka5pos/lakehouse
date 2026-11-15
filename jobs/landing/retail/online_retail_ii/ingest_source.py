import requests
import boto3
import os

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx"

response = requests.get(url)
response.raise_for_status()

s3 = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-east-1"
)

s3.put_object(
    Bucket="warehouse",
    Key="landing/retail/online_retail_ii/source.xlsx",
    Body=response.content,
    ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

print("Source file uploaded successfully")