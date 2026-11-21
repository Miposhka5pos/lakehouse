#!/usr/bin/env sh
set -eu

CLASSPATH="/usr/lib/iceberg-rest/iceberg-rest-adapter.jar:/usr/lib/iceberg-rest/postgresql-42.7.14.jar"

if [ -n "${LOG_CONFIG_DIR:-}" ]; then
  CLASSPATH="${LOG_CONFIG_DIR}:${CLASSPATH}"
fi

set -- java

if [ -n "${LOG_LEVEL:-}" ]; then
  set -- "$@" "-Dorg.slf4j.simpleLogger.defaultLogLevel=${LOG_LEVEL}"
fi

exec "$@" -cp "$CLASSPATH" org.apache.iceberg.rest.RESTCatalogServer
