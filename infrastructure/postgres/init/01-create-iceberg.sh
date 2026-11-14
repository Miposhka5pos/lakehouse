#!/bin/bash
set -e

psql \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=db_user="$ICEBERG_DB_USER" \
  --set=db_password="$ICEBERG_DB_PASSWORD" \
  --set=db_name="$ICEBERG_DB_NAME" <<'SQL'
CREATE ROLE :"db_user" LOGIN PASSWORD :'db_password';
CREATE DATABASE :"db_name" OWNER :"db_user";
SQL