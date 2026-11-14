FROM apache/iceberg-rest-fixture

USER root

RUN curl -fL \
    https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.14/postgresql-42.7.14.jar \
    -o /usr/lib/iceberg-rest/postgresql-42.7.14.jar \
    && chown iceberg:iceberg /usr/lib/iceberg-rest/postgresql-42.7.14.jar

USER iceberg:iceberg

CMD ["java", "-cp", "/usr/lib/iceberg-rest/iceberg-rest-adapter.jar:/usr/lib/iceberg-rest/postgresql-42.7.14.jar", "org.apache.iceberg.rest.RESTCatalogServer"]