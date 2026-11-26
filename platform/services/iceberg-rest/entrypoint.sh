#!/usr/bin/env sh
set -eu

CLASSPATH="/opt/iceberg-rest/lib/*"

if [ -n "${LOG_CONFIG_DIR:-}" ]; then
    CLASSPATH="${LOG_CONFIG_DIR}:${CLASSPATH}"
fi

set -- java

if [ -n "${LOG_LEVEL:-}" ]; then
    set -- "$@" "-Dorg.slf4j.simpleLogger.defaultLogLevel=${LOG_LEVEL}"
fi

exec "$@" \
    -cp "$CLASSPATH" \
    org.apache.iceberg.rest.RESTCatalogServer
