
FROM gradle:8.14.3-jdk11 AS builder

WORKDIR /workspace

COPY runtime/ ./

RUN gradle --no-daemon copyRestRuntime


FROM eclipse-temurin:11-jre-jammy

USER root

ENV JAVA_HOME=/opt/java/openjdk
ENV HADOOP_CONF_DIR=/opt/hadoop-conf
ENV REST_HOME=/opt/iceberg-rest

RUN groupadd --system iceberg \
    && useradd --system \
       --gid iceberg \
       --home-dir /opt/iceberg-rest \
       --shell /usr/sbin/nologin \
       iceberg \
    && mkdir -p \
       /opt/iceberg-rest/lib \
       /opt/hadoop-conf \
    && chown -R iceberg:iceberg /opt/iceberg-rest

COPY --from=builder /workspace/build/rest-runtime/ /opt/iceberg-rest/lib/

COPY entrypoint.sh /usr/local/bin/iceberg-rest-entrypoint

RUN sed -i 's/\r$//' /usr/local/bin/iceberg-rest-entrypoint \
    && chmod 755 /usr/local/bin/iceberg-rest-entrypoint \
    && chown -R iceberg:iceberg /opt/iceberg-rest

USER iceberg:iceberg

EXPOSE 8181

ENTRYPOINT ["/usr/local/bin/iceberg-rest-entrypoint"]
