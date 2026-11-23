
FROM apache/airflow:3.1.8

# Java нужна для запуска Spark client
USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Устанавливаем Python-зависимости от имени airflow
USER airflow

COPY --chown=airflow:root services/airflow/requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir \
    "apache-airflow==3.1.8" \
    -r /tmp/requirements.txt

# Создаём команду spark-submit после установки PySpark
USER root

RUN cat > /usr/local/bin/spark-submit <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

PYSPARK_SUBMIT="$(python -c 'import pathlib, pyspark; print(pathlib.Path(pyspark.__file__).parent / "bin" / "spark-submit")')"

exec "$PYSPARK_SUBMIT" "$@"
EOF

RUN chmod 755 /usr/local/bin/spark-submit

USER airflow
