
# syntax=docker/dockerfile:1.7
FROM lakehouse-hadoop:3.4.3

USER root

ARG SPARK_VERSION=3.5.10

ENV SPARK_HOME=/opt/spark
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV PYSPARK_PYTHON=/opt/conda/bin/python3
ENV PATH="${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

# Install Apache Spark without bundled Hadoop.
RUN mkdir -p "${SPARK_HOME}" \
    && curl -fL \
       "https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-without-hadoop.tgz" \
       -o /tmp/spark.tgz \
    && tar -xzf /tmp/spark.tgz \
       --strip-components=1 -C "${SPARK_HOME}" \
    && rm -f /tmp/spark.tgz

# Install Jupyter Notebook.
RUN python3 -m pip install --no-cache-dir notebook==7.3.2

# Use Hadoop 3.4.3 libraries from the base image.
RUN cat > "${SPARK_HOME}/conf/spark-env.sh" <<'EOF'
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-/opt/hadoop/etc/hadoop}"
export SPARK_DIST_CLASSPATH="$("${HADOOP_HOME}/bin/hadoop" classpath)"
EOF

# Prepare Spark and Jupyter directories.
RUN mkdir -p \
    /home/iceberg/notebooks \
    /home/iceberg/spark-events \
    "${SPARK_HOME}/logs" \
    "${SPARK_HOME}/work" \
    && chown -R hadoop:users \
       /home/iceberg \
       "${SPARK_HOME}"

# Start PySpark with Jupyter Notebook.
RUN cat > /usr/local/bin/notebook <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --notebook-dir=/home/iceberg/notebooks --ip=0.0.0.0 --ServerApp.token='' --ServerApp.password='' --port=8888 --no-browser"

exec /opt/spark/bin/pyspark "$@"
EOF

# Normalize Windows line endings in generated scripts.
RUN sed -i 's/\r$//' \
    "${SPARK_HOME}/conf/spark-env.sh" \
    /usr/local/bin/notebook

RUN chmod 755 /usr/local/bin/notebook

USER hadoop
