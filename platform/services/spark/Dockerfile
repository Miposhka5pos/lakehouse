
FROM tabulario/spark-iceberg@sha256:790a72e744e0d09f161e1b4c7c2f79625cc598cf0476da4703e62f1f4e023460

USER root

RUN chmod 755 /bin/notebook

# Create the same runtime identity used by Hadoop containers.
RUN groupadd --gid 1000 hadoop \
    && useradd --uid 1000 --gid 1000 \
       --create-home --home-dir /home/hadoop \
       --shell /bin/bash hadoop

# Prepare writable directories for Spark and Jupyter.
RUN mkdir -p \
    /home/iceberg/spark-events \
    /opt/spark/logs \
    /opt/spark/work \
    && chown -R hadoop:hadoop \
       /home/iceberg \
       /home/hadoop \
       /opt/spark/logs \
       /opt/spark/work

USER hadoop
