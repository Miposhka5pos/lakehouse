# Спецификация проекта Lakehouse

**Дата среза:** 2026-11-27  
**Репозиторий:** https://github.com/Miposhka5pos/lakehouse  
**Ветка:** main  
**Базовый commit:** ef94aec3cba43a9935177b9144d13a920fd73545

> Документ предназначен для разработчиков, операторов и AI-ассистентов как основная точка входа в контекст проекта. Он описывает подтверждённое кодом текущее состояние и отдельно отмечает предложения и неизвестные детали. Если текст расходится с актуальным кодом, сначала зафиксируйте расхождение и проверьте код; не считайте предположение фактом.

## 1. Краткое описание

Lakehouse — проект аналитической платформы на открытом стеке. В текущей реализации построен batch-пайплайн для набора Online Retail II: Excel-файл с двумя годовыми листами загружается в Bronze, типизируется и очищается в Silver, после чего формируются четыре аналитические витрины Gold.

Подтверждённый технологический контур:
- Apache Airflow — описание и запуск DAG;
- Apache Spark / PySpark — распределённая обработка;
- Apache Hadoop HDFS — файловое хранилище;
- Hadoop YARN — управление ресурсами и запуск Spark;
- Apache Iceberg — табличный формат;
- Iceberg REST Catalog — каталог метаданных;
- PostgreSQL — backend метаданных каталога (по истории коммитов — PostgreSQL-backed JdbcCatalog);
- Spark Excel connector — чтение XLSX.

Проект нельзя пока считать полностью production-ready: в ETL-коде видны базовые загрузки и трансформации, но не подтверждены полноценные CI/CD, мониторинг качества, SLA, инкрементальные загрузки, lineage, backup/restore и production security.

## 2. Цели и границы

### 2.1. Реализованные цели
1. Читать листы Year 2009-2010 и Year 2010-2011 из Online Retail II XLSX.
2. Сохранять исходные значения в Bronze преимущественно строковыми полями.
3. Преобразовывать значения в типизированную Silver-таблицу.
4. Строить витрины по клиентам, месяцам и странам, товарам и продажам товаров.
5. Хранить данные в Iceberg, а файлы таблиц — в HDFS.
6. Запускать Spark jobs из Airflow через SparkSubmitOperator в YARN cluster mode.

### 2.2. Не подтверждено как реализованное
Streaming, CDC, API для потребителей, BI-дашборды, автоматическое расписание, автоматическая связь отдельных DAG Bronze/Silver/Gold, инкрементальные merge/upsert, обработка late-arriving events, multi-tenancy, полноценная RBAC-модель, schema registry, disaster recovery. Не описывайте эти функции как существующие без проверки кода.

## 3. Технологии и версии

| Компонент | Роль | Что подтверждено |
|---|---|---|
| Airflow | Оркестрация | DAG и SparkSubmitOperator |
| Spark | Вычисления | ветка 3.5.x; история обновления указывает 3.5.10 |
| Hadoop | HDFS/YARN | история обновления указывает 3.4.3 и Java 11 |
| Iceberg | Табличный формат | Spark runtime 1.10.2 |
| Iceberg REST | Каталог | http://rest:8181 внутри сети |
| HDFS | Хранилище | hdfs://namenode:9000 |
| PostgreSQL | Метаданные каталога | JdbcCatalog backend по истории коммитов |
| Spark Excel | Чтение XLSX | com.crealytics:spark-excel_2.12:3.5.1_0.20.4 |

Версии Airflow, Python, PostgreSQL, Docker images и других зависимостей здесь не зафиксированы, поскольку их нельзя надёжно вывести из рассмотренных ETL-файлов. Источником истины для них должны быть manifests, Dockerfiles и compose-конфигурации.

## 4. Архитектура

### 4.1. Поток данных

```text
Online Retail II source.xlsx
        |
        v
HDFS landing:
 /warehouse/landing/retail/online_retail_ii/source.xlsx
        |
        v
Airflow DAG: retail_online_retail_ii_bronze
        |
        v
Spark on YARN (cluster mode)
        |
        v
Iceberg REST Catalog (catalog name: demo)
        |
        +---- PostgreSQL metadata backend
        |
        v
HDFS warehouse: /warehouse
        |
        v
demo.bronze.online_retail_ii
        |
        v
Airflow DAG: retail_online_retail_ii_silver
        |
        v
demo.silver.online_retail_ii
        |
        v
Airflow DAG: retail_online_retail_ii_gold
        |
        +--> demo.gold.customer_performance
        +--> demo.gold.monthly_sales_by_country
        +--> demo.gold.product_performance
        +--> demo.gold.product_sales
```

### 4.2. HDFS и Iceberg

Подтверждённые настройки Spark catalog:
- имя каталога: demo;
- type: rest;
- URI: http://rest:8181;
- FileIO: org.apache.iceberg.hadoop.HadoopFileIO;
- warehouse: hdfs://namenode:9000/warehouse;
- default catalog: demo;
- Spark SQL extension: org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions.

HDFS defaultFS: hdfs://namenode:9000. Landing-файл ожидается по пути, указанному выше. Spark staging directory: hdfs://namenode:9000/tmp/spark-staging. В Bronze DAG включены Spark event logs в hdfs://namenode:9000/spark-events.

Переход с MinIO/S3 на HDFS и HadoopFileIO подтверждён историей коммитов. Не добавляйте обратно S3A/MinIO параметры без отдельного архитектурного решения.

### 4.3. YARN

В Bronze DAG явно заданы:
- ResourceManager hostname: resourcemanager;
- ResourceManager address: resourcemanager:8032;
- spark.yarn.submit.waitAppCompletion=true;
- deploy_mode=cluster;
- staging directory в HDFS.

Текущие параметры ресурсов Bronze: один executor, один core, 1g executor memory, один driver core, 1g driver memory. Это конфигурация текущего задания, а не универсальная рекомендация для production.

### 4.4. Ответственность компонентов

- Airflow хранит DAG и управляет запуском.
- Spark выполняет чтение, преобразования и SQL-агрегации.
- YARN выделяет ресурсы и запускает Spark application.
- HDFS хранит landing-файл, staging, event logs и Iceberg data files.
- REST Catalog предоставляет метаданные Iceberg.
- PostgreSQL хранит backend метаданных каталога.

## 5. Структура кода

Подтверждённые основные пути:

```text
applications/airflow/
  dags/retail/
    retail_online_retail_ii_bronze.py
    retail_online_retail_ii_silver.py
    retail_online_retail_ii_gold.py
  spark/jobs/
    bronze/retail/online_retail_ii/build_online_retail_ii.py
    silver/retail/online_retail_ii/build_online_retail_ii.py
    gold/retail/
      customer_performance/build_customer_performance.py
      monthly_sales_by_country/build_monthly_sales.py
      product_performance/build_product_performance.py
      product_sales/build_product_sales.py
```

DAG определяют параметры запуска Spark. Jobs содержат собственно обработку данных и SQL. В репозитории могут присутствовать и другие инфраструктурные файлы; перед изменением окружения изучайте их фактическое содержимое.

## 6. Источник и входной контракт

Источник: XLSX Online Retail II в HDFS:

hdfs://namenode:9000/warehouse/landing/retail/online_retail_ii/source.xlsx

Ожидаемые листы:
- Year 2009-2010
- Year 2010-2011

Исходные колонки:
- Invoice
- StockCode
- Description
- Quantity
- InvoiceDate
- Price
- Customer ID
- Country

В Bronze для этих колонок задан nullable StringType. Customer ID переименовывается в Customer_ID. Для каждого листа добавляются:
- source_sheet — имя листа;
- source_file — путь к исходному файлу;
- ingested_at — current_timestamp().

Листы объединяются через unionByName. Для чтения используется Spark Excel connector, header=true, dataAddress начинается с A1, задана явная схема.

Ограничения текущего контракта:
- путь, имя файла, листы и схема зафиксированы в коде;
- автоматического обнаружения новых файлов/листов не видно;
- checksum и версия исходного файла не фиксируются;
- повторная загрузка перезаписывает таблицу через createOrReplace();
- обработку повреждённого файла, пустого листа и изменения заголовков нужно отдельно проверить.

## 7. Модель данных

### 7.1. Bronze: demo.bronze.online_retail_ii

Назначение: исходная зона с минимальной трансформацией и строковыми значениями бизнес-полей.

| Поле | Тип | Семантика |
|---|---|---|
| Invoice | string | Номер счёта |
| StockCode | string | Код товара |
| Description | string | Описание товара |
| Quantity | string | Исходное количество |
| InvoiceDate | string | Исходная дата/время |
| Price | string | Исходная цена |
| Customer_ID | string | ID клиента после переименования |
| Country | string | Страна |
| source_sheet | string | Исходный лист |
| source_file | string | Путь к источнику |
| ingested_at | timestamp | Время загрузки |

Iceberg tableProperty format-version задан как 2. Запись — createOrReplace().

### 7.2. Silver: demo.silver.online_retail_ii

Источник: Bronze. Поля и преобразования:
- Invoice → trim → invoice;
- StockCode → trim → stock_code;
- Description → trim → description;
- Quantity → int → quantity;
- InvoiceDate → to_timestamp с форматом M/d/yy H:mm → invoice_date;
- Price → DecimalType(10,2) → price;
- Customer_ID → int → customer_id;
- Country → trim → country;
- source_sheet сохраняется.

Silver считает и выводит:
- total_rows;
- null_invoice_date;
- null_quantity;
- null_price;
- null_customer_id.

Метрики только печатаются. Порогов, quarantine или блокировки публикации в рассматриваемом коде нет. Таблица записывается через createOrReplace(). source_file и ingested_at в Silver не переносятся — это факт текущей реализации, не обязательно целевое решение.

### 7.3. Gold: demo.gold.customer_performance

Гранулярность: одна запись на customer_id. Источник: Silver. NULL customer_id исключается.

Поля:
- customer_id;
- invoices_count = COUNT(DISTINCT invoice);
- items_sold = SUM(quantity);
- revenue = SUM(quantity * price);
- avg_invoice_value = revenue / invoices_count, округление до 2 знаков, NULLIF защищает от нулевого делителя;
- first_purchase = MIN(invoice_date);
- last_purchase = MAX(invoice_date).

### 7.4. Gold: demo.gold.monthly_sales_by_country

Гранулярность: месяц × country.

Поля:
- sales_month = DATE_TRUNC('MONTH', invoice_date);
- country;
- invoices_count = COUNT(DISTINCT invoice);
- customers_count = COUNT(DISTINCT customer_id);
- items_sold = SUM(quantity);
- revenue = SUM(quantity * price).

Отдельного фильтра NULL customer_id нет; COUNT(DISTINCT ...) не учитывает NULL, остальные агрегаты могут включать соответствующие строки.

### 7.5. Gold: demo.gold.product_performance

Гранулярность: stock_code.

Поля:
- stock_code;
- invoices_count = COUNT(DISTINCT invoice);
- customers_count = COUNT(DISTINCT customer_id);
- items_sold = SUM(quantity);
- revenue = SUM(quantity * price).

### 7.6. Gold: demo.gold.product_sales

Гранулярность: stock_code × description.

Поля:
- stock_code;
- description;
- invoices_count;
- customers_count;
- items_sold;
- revenue;
- avg_unit_price = revenue / items_sold, округление до 2 знаков, NULLIF для нулевого знаменателя.

Каждая Gold job создаёт namespace demo.gold при необходимости, читает Silver, записывает результат через createOrReplace(), выводит количество строк.

## 8. Оркестрация

DAG:
- retail_online_retail_ii_bronze;
- retail_online_retail_ii_silver;
- retail_online_retail_ii_gold.

У DAG schedule=None и catchup=False: автоматического расписания из этих определений не следует. Запуск ручной либо внешним механизмом.

Внутри Gold DAG задачи связаны последовательно:

```text
build_customer_performance
  -> build_monthly_sales
  -> build_product_performance
  -> build_product_sales
```

Важно: это последовательный запуск, не параллельный. Между отдельными DAG Bronze, Silver и Gold зависимость в их коде не выражена. Нельзя утверждать, что запуск Gold автоматически запускает Silver или Bronze.

Параметры:
- Bronze: owner=data-engineering, retries=0, start_date 2025-01-01 UTC;
- Silver: retries=0, start_date 2025-01-01;
- Gold: retries=0, max_active_runs=1, start_date 2025-01-01.

Проверьте timezone Airflow: Bronze использует timezone-aware UTC, Silver и Gold — datetime без timezone.

## 9. Предпосылки запуска

До выполнения должны быть доступны:
1. Airflow scheduler/webserver и executor.
2. Airflow connection spark_default с корректными параметрами подключения к Spark/YARN.
3. YARN ResourceManager и NodeManager.
4. HDFS NameNode и DataNode.
5. Iceberg REST Catalog на rest:8181.
6. PostgreSQL backend каталога.
7. XLSX по ожидаемому HDFS path.
8. Spark runtime и необходимые packages на стороне submit/cluster.

Рекомендуемый ручной порядок:
1. Проверить наличие исходного файла в HDFS.
2. Запустить Bronze DAG.
3. Проверить demo.bronze.online_retail_ii и число строк.
4. Запустить Silver DAG.
5. Проверить demo.silver.online_retail_ii и метрики качества.
6. Запустить Gold DAG.
7. Проверить все четыре Gold-таблицы и сверить агрегаты с Silver.

Bronze DAG содержит наиболее полную конфигурацию YARN/HDFS/Iceberg. Silver и Gold DAG передают более короткий набор параметров; jobs отдельно конфигурируют Iceberg catalog. При изменении инфраструктуры нужно проверить фактическую доступность одинаковых настроек во всех режимах запуска.

## 10. Нефункциональные требования и инженерные правила

Ниже — целевые требования для развития, не утверждение, что они уже полностью реализованы.

### Надёжность
- повторный запуск должен иметь документированную и предсказуемую семантику;
- инфраструктурные ошибки должны приводить к ненулевому статусу;
- логировать run id, источник, целевую таблицу и row counts;
- не подавлять исключения;
- закрывать SparkSession через try/finally.

### Качество данных
- определить обязательность полей и допустимые NULL;
- установить пороги для метрик и правила остановки;
- фиксировать row counts на каждом этапе;
- тестировать гранулярность и уникальность Gold;
- явно определить бизнес-смысл возвратов/отмен и отрицательных quantity.

### Производительность
- подбирать ресурсы по объёму данных и ресурсам кластера;
- не считать настройки 1 executor/1g универсальными;
- выбирать Iceberg partitioning после анализа запросов;
- избегать повторного вычисления lineage без необходимости.

### Безопасность
- не коммитить пароли, токены, ключи и реальные credentials;
- ограничить сетевой доступ к HDFS/YARN/Catalog/PostgreSQL;
- рассмотреть TLS, аутентификацию и авторизацию для production;
- определить ACL для landing, warehouse и staging;
- считать customer identifiers чувствительными данными и применять минимальные привилегии.

### Поддерживаемость
- вынести повторяющиеся Spark/Iceberg настройки в общий конфигурационный слой;
- согласовывать Spark, Scala binary version, Iceberg runtime и Hadoop runtime;
- описывать схему, гранулярность, источник и quality rules каждой таблицы;
- обновлять документацию вместе с кодом.

## 11. Риски и вопросы для проверки

1. Между DAG нет явной зависимости Bronze → Silver → Gold.
2. Расписание не задано; запуск не автоматизирован.
3. retries=0; временные сбои не повторяются автоматически.
4. Silver quality metrics не блокируют публикацию при плохих значениях.
5. createOrReplace() означает полную замену результата; инкрементальная история не реализована в этих jobs.
6. Конфигурация Spark частично дублируется между DAG и jobs.
7. Парсер даты жёстко использует M/d/yy H:mm; некорректные значения становятся NULL.
8. Ошибки cast для числовых полей могут превращаться в NULL; quarantine не виден.
9. Выручка считается как SUM(quantity * price) без отдельной классификации возвратов/отмен.
10. Политика NULL для разных витрин неодинакова.
11. Контракт зависит от фиксированных XLSX листов и заголовков.
12. В Bronze cleanup реализован через finally; Silver/Gold вызывают spark.stop() в конце, без общей finally-защиты.
13. Gold витрины выполняются последовательно; нужно подтвердить, что это осознанное требование.
14. Timezone DAG отличается по способу задания.
15. Наличие/отсутствие тестов во всём репозитории нельзя заключать только по ETL-файлам — проверить полную структуру.

## 12. План развития

Предлагаемые приоритеты, не текущий функционал.

### P0 — воспроизводимость
- README с prerequisites и локальным запуском;
- единый реестр версий;
- инструкция по Airflow connection spark_default;
- smoke tests HDFS/YARN/REST Catalog/PostgreSQL;
- процедура загрузки и проверки исходного XLSX.

### P1 — корректность
- связать Bronze → Silver → Gold master DAG или Dataset scheduling;
- настроить retry/backoff;
- сделать quality gates;
- сохранять quality metrics в таблицу/систему наблюдаемости;
- определить правила NULL, возвратов, отмен и отрицательных quantity;
- гарантировать Spark cleanup через try/finally.

### P2 — инженерная зрелость
- unit/integration tests для трансформаций;
- тесты схем Iceberg и бизнес-агрегатов на fixture data;
- CI: lint, formatting, DAG import test, unit tests;
- единые logging и Spark config;
- lineage и run metadata;
- владельцы данных и документация контрактов.

### P3 — эксплуатация и масштабирование
- Iceberg partitioning/sort order по workload;
- compaction и обслуживание snapshots/orphan files;
- backup/restore HDFS и PostgreSQL;
- мониторинг Airflow/YARN/Spark/HDFS и алерты;
- SLA/SLO, RPO/RTO и runbooks;
- оценка incremental processing вместо полного replace.

## 13. Тестовая стратегия

**Bronze**
- оба листа читаются;
- заголовки и схема соответствуют контракту;
- Customer ID переименован;
- source_sheet/source_file/ingested_at заполнены;
- union не теряет строки;
- повторный запуск даёт ожидаемый результат.

**Silver**
- trim применяется к строковым полям;
- quantity/customer_id имеют integer тип;
- price имеет decimal(10,2);
- invoice_date парсится на валидных примерах;
- невалидные значения дают ожидаемые NULL и метрики;
- схема совпадает с контрактом.

**Gold**
- проверена гранулярность каждой витрины;
- distinct invoice/customer считается корректно;
- revenue и средние значения сверены вручную на маленьком наборе;
- NULL customer_id обрабатывается согласно контракту;
- нулевой знаменатель не вызывает ошибку;
- Gold агрегаты сверяются с Silver.

**Интеграция**
- DAG импортируются Airflow;
- SparkSubmitOperator использует spark_default;
- Spark job читает HDFS и REST Catalog;
- Iceberg table создаётся и читается повторно;
- downstream не стартует при падении upstream после введения оркестрации.

## 14. Инструкции AI-ассистентам и новым участникам

Этот раздел обязателен к прочтению перед любыми изменениями.

1. Сначала прочитай этот документ, затем README, compose/Dockerfiles, manifests зависимостей, DAG, Spark jobs и последние коммиты.
2. Проект этого репозитория — Lakehouse. Не смешивай его с другими темами пользовательских разговоров.
3. Всегда разделяй факт текущего кода, вывод из истории, предположение и предложение.
4. Не описывай roadmap как реализованную функцию.
5. При изменении схем Bronze/Silver/Gold обновляй спецификацию и тесты.
6. Перед изменением версий проверяй совместимость Spark 3.5, Scala 2.12, Iceberg runtime и Hadoop.
7. Не придумывай переменные окружения, сервисы, порты, credentials, пути и команды — найди их в репозитории.
8. Не коммить секреты и персональные данные.
9. Не меняй бизнес-метрики без описания определения и тестов.
10. Не предполагай автоматические зависимости DAG, если они не выражены кодом.
11. В отчёте о работе указывай изменённые файлы, проверки, непроверенные части и оставшиеся риски.
12. При расхождении кода и документа фиксируй расхождение и синхронизируй оба источника после проверки.
13. Для новой таблицы обязательно описывай полное имя, назначение, владельца, источник, гранулярность, поля/типы/nullability, дедупликацию, NULL policy, стратегию обновления, partitioning, quality checks, потребителей и SLA.

## 15. Глоссарий

- Lakehouse — архитектура, сочетающая подходы data lake и аналитического хранилища.
- HDFS — распределённая файловая система Hadoop.
- YARN — менеджер ресурсов Hadoop.
- Spark — распределённый вычислительный движок.
- Iceberg — табличный формат с метаданными, snapshots и эволюцией схем.
- REST Catalog — сервис каталога таблиц Iceberg.
- Bronze — слой исходных данных с минимальными преобразованиями.
- Silver — очищенный и типизированный слой.
- Gold — предметные аналитические витрины.
- DAG — направленный ациклический граф задач Airflow.
- Data quality — проверки полноты, корректности и согласованности данных.

## 16. Основные источники истины в коде

- applications/airflow/dags/retail/retail_online_retail_ii_bronze.py
- applications/airflow/dags/retail/retail_online_retail_ii_silver.py
- applications/airflow/dags/retail/retail_online_retail_ii_gold.py
- applications/airflow/spark/jobs/bronze/retail/online_retail_ii/build_online_retail_ii.py
- applications/airflow/spark/jobs/silver/retail/online_retail_ii/build_online_retail_ii.py
- applications/airflow/spark/jobs/gold/retail/customer_performance/build_customer_performance.py
- applications/airflow/spark/jobs/gold/retail/monthly_sales_by_country/build_monthly_sales.py
- applications/airflow/spark/jobs/gold/retail/product_performance/build_product_performance.py
- applications/airflow/spark/jobs/gold/retail/product_sales/build_product_sales.py

История коммитов дополнительно подтверждает миграцию MinIO/S3 → HDFS/HadoopFileIO, использование HDFS warehouse, PostgreSQL-backed Iceberg JdbcCatalog, обновление Hadoop/Spark/Iceberg и запуск Spark jobs в YARN cluster mode.

---

**Статус:** архитектурно-функциональная спецификация текущего состояния по коду на дату среза. Документ не заменяет deployment runbook. Для полного воспроизведения окружения дополнительно сверьте актуальные Docker/Compose-конфигурации и manifests зависимостей.
