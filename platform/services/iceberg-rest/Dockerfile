
FROM apache/iceberg-rest-fixture

USER root

ARG HADOOP_VERSION=3.3.6

RUN curl -fL \
    "https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-client-api/${HADOOP_VERSION}/hadoop-client-api-${HADOOP_VERSION}.jar" \
    -o /usr/lib/iceberg-rest/hadoop-client-api.jar \
    && curl -fL \
    "https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-client-runtime/${HADOOP_VERSION}/hadoop-client-runtime-${HADOOP_VERSION}.jar" \
    -o /usr/lib/iceberg-rest/hadoop-client-runtime.jar \
    && curl -fL \
    "https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-hdfs-client/${HADOOP_VERSION}/hadoop-hdfs-client-${HADOOP_VERSION}.jar" \
    -o /usr/lib/iceberg-rest/hadoop-hdfs-client.jar \
    && curl -fL \
    https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.14/postgresql-42.7.14.jar \
    -o /usr/lib/iceberg-rest/postgresql-42.7.14.jar \
    && chown iceberg:iceberg /usr/lib/iceberg-rest/*.jar

USER iceberg:iceberg

CMD ["java", "-cp", "/usr/lib/iceberg-rest/iceberg-rest-adapter.jar:/usr/lib/iceberg-rest/postgresql-42.7.14.jar:/usr/lib/iceberg-rest/hadoop-client-api.jar:/usr/lib/iceberg-rest/hadoop-client-runtime.jar:/usr/lib/iceberg-rest/hadoop-hdfs-client.jar", "org.apache.iceberg.rest.RESTCatalogServer"]
