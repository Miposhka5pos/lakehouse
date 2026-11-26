# Согласованные версии Lakehouse

**Статус:** целевая конфигурация для следующего этапа обновления. Этот документ фиксирует версии, но сам по себе не меняет Docker-образы, Compose-файлы или DAG-и.

## Целевой стек

| Компонент | Целевая версия | Примечание |
|---|---:|---|
| Java | 17 LTS | Одна согласованная major-версия в Hadoop/YARN, Spark driver и executors, Iceberg REST Catalog |
| Apache Hadoop | 3.5.0 | Серверная часть Hadoop 3.5 требует Java 17 |
| Apache Spark | 3.5.10 | Последний maintenance-релиз ветки 3.5 на дату фиксации |
| Scala | 2.12 | Использовать Spark-сборку и все Scala-артефакты с суффиксом `_2.12` |
| Apache Iceberg | 1.12.0 | Использовать runtime `iceberg-spark-runtime-3.5_2.12` |
| Iceberg REST Catalog | 1.12.0 | Версию сервера согласовать с клиентской библиотекой Iceberg |
| Apache Airflow | 3.1.8 | Сохранить текущую линию Airflow; Python 3.10 входит в поддерживаемые версии |
| Python | 3.10.x | Одинаковая совместимая версия в Airflow и YARN-контейнерах; Python 3.10.14 уже проверен в NodeManager |
| spark-excel | `3.5.1_0.20.4` | Текущий координат Maven; отдельно проверить чтение XLSX на Spark 3.5.10 |

Для Java следует использовать поддерживаемый дистрибутив JDK 17 LTS (например, Eclipse Temurin). Конкретный patch/build JDK нужно закрепить в Dockerfile при обновлении образов, а не оставлять плавающий тег.

## Почему выбраны эти версии

- Hadoop 3.5.0 требует Java 17 на серверной стороне.
- Spark 3.5.10 — maintenance-релиз ветки Spark 3.5; ветка сохраняет совместимость с Scala 2.12.
- Iceberg 1.12.0 публикует runtime для Spark 3.5 и Scala 2.12.
- Airflow 3.1.8 поддерживает Python 3.10–3.13, поэтому Python 3.10 можно оставить общей версией для оркестрации и Spark-приложения.

## Правила согласования

1. Java major-версия должна совпадать во всех JVM-процессах YARN: ResourceManager, NodeManager, Spark driver и executors. Для выбранного стека это Java 17.
2. Spark и Iceberg runtime должны совпадать по линии Spark и бинарной версии Scala: `spark-3.5` и `_2.12`.
3. Iceberg runtime JAR и Iceberg REST Catalog server следует обновлять согласованно до 1.12.0.
4. Не смешивать версии Spark из разных контейнеров. Spark client, Spark driver и executors должны использовать одну версию 3.5.10.
5. Версии PostgreSQL фиксируются отдельно для каждого сервиса. В текущем Compose обнаружены одновременно образы PostgreSQL 16 и 17; до отдельной проверки совместимости их нельзя считать единой версией платформы.
6. Версии в этом документе — целевое состояние, а не утверждение, что образы уже обновлены. После изменения Dockerfiles и Compose фактические версии нужно проверить внутри контейнеров и в YARN application logs.

## Исходное состояние, выявленное при диагностике

| Компонент | Обнаружено |
|---|---|
| Airflow image | `lakehouse-airflow:3.1.8-spark-3.5.5` |
| Spark image | `lakehouse-spark:3.5.5` |
| Hadoop image | `lakehouse-hadoop:3.3.6` |
| Iceberg runtime | `1.8.1` |
| Java в YARN NodeManager | OpenJDK `1.8.0_212` |
| Python в YARN NodeManager | `3.10.14` |
| PostgreSQL images | `16-alpine` и `17-alpine` |

Последняя ошибка Spark job была вызвана несовместимостью JVM: Iceberg-класс `org.apache.iceberg.spark.ExtendedParser` имел class-file version 55 (Java 11), а YARN-контейнер запускал Java 8, которая поддерживает class-file version не выше 52.

## Источники

- [Apache Hadoop 3.5.0 — Java 17 support](https://hadoop.apache.org/docs/r3.5.0/)
- [Apache Spark 3.5.10 — release notes](https://spark.apache.org/releases/spark-release-3-5-10.html)
- [Apache Spark — downloads and Scala artifacts](https://spark.apache.org/downloads.html)
- [Apache Iceberg 1.12.0 — release notes](https://iceberg.apache.org/blog/apache-iceberg-1.12.0-release/)
- [Apache Iceberg — supported engine versions and runtime artifacts](https://iceberg.apache.org/multi-engine-support/)
- [Apache Airflow 3.1.8 — supported Python versions](https://airflow.apache.org/docs/apache-airflow/3.1.8/installation/supported-versions.html)

Дата фиксации: 2026-11-26.
