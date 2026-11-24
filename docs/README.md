# Lakehouse — документация и управление

## Сервисы и интерфейсы

Все адреса ниже рассчитаны на локальный запуск Docker Compose на этой машине.

| Сервис | Интерфейс / адрес | Назначение |
|---|---|---|
| Airflow | [http://localhost:8081](http://localhost:8081) | Управление DAG-ами и просмотр запусков |
| MinIO Console | [http://localhost:9001](http://localhost:9001) | Веб-интерфейс объектного хранилища |
| MinIO S3 API | [http://localhost:9000](http://localhost:9000) | S3 endpoint для приложений и клиентов |
| Iceberg REST Catalog | [http://localhost:8181](http://localhost:8181) | REST API каталога Apache Iceberg |
| Spark UI | [http://localhost:8080](http://localhost:8080) | Веб-интерфейс Spark, предоставляемый Spark-контейнером |
| Jupyter Notebook | [http://localhost:8888](http://localhost:8888) | Notebook-интерфейс Spark-контейнера |
| PostgreSQL (Iceberg catalog) | `localhost:5432` | PostgreSQL; подключение SQL-клиентом |
| Spark port | `localhost:10000`, `localhost:10001` | Дополнительные порты, опубликованные Spark-контейнером; назначение зависит от конфигурации образа |

PostgreSQL Airflow доступен только внутри Docker-сети и не публикует порт на хост.

### Внутренние адреса Docker-сети

Контейнеры обращаются друг к другу по именам сервисов, а не через `localhost`:

| Зависимость | Внутренний адрес |
|---|---|
| MinIO S3 API | `http://minio:9000` |
| Iceberg REST Catalog | `http://rest:8181` |
| Spark Master | `spark://spark-iceberg:7077` |
| PostgreSQL Iceberg | `postgres:5432` |
| PostgreSQL Airflow | `airflow-postgres:5432` |

## Управление Docker Compose

Команды выполняются из корня репозитория. Основной Compose-файл подключает Airflow Compose через `include`, поэтому обычно достаточно одного файла:

```powershell
# Проверить итоговую конфигурацию Compose
docker compose -f platform/deployment/docker-compose.yml config

# Собрать образы и запустить все сервисы в фоне
docker compose -f platform/deployment/docker-compose.yml up -d --build

# Посмотреть состояние сервисов
docker compose -f platform/deployment/docker-compose.yml ps

# Посмотреть логи всех сервисов
docker compose -f platform/deployment/docker-compose.yml logs -f

# Логи конкретного сервиса
docker compose -f platform/deployment/docker-compose.yml logs -f airflow-scheduler

# Перезапустить все сервисы
docker compose -f platform/deployment/docker-compose.yml restart

# Перезапустить один сервис
docker compose -f platform/deployment/docker-compose.yml restart airflow-scheduler

# Остановить и удалить контейнеры и сеть проекта
docker compose -f platform/deployment/docker-compose.yml down
```

`down` не удаляет именованные volumes с данными. Не добавляйте `-v`, если намеренно не хотите удалить volumes и хранящиеся в них данные.

### Имена сервисов для адресных команд

| Компонент | Compose service |
|---|---|
| PostgreSQL для Iceberg | `postgres` |
| MinIO | `minio` |
| Iceberg REST Catalog | `rest` |
| Spark | `spark` |
| PostgreSQL для Airflow | `airflow-postgres` |
| Airflow initialization | `airflow-init` |
| Airflow API server | `airflow-apiserver` |
| Airflow Scheduler | `airflow-scheduler` |
| Airflow DAG Processor | `airflow-dag-processor` |

Примеры операций с отдельными сервисами:

```powershell
# Запустить или пересоздать один сервис
docker compose -f platform/deployment/docker-compose.yml up -d minio

# Остановить один сервис
docker compose -f platform/deployment/docker-compose.yml stop spark

# Выполнить команду внутри контейнера
docker compose -f platform/deployment/docker-compose.yml exec airflow-scheduler airflow dags list

# Открыть shell внутри контейнера
docker compose -f platform/deployment/docker-compose.yml exec airflow-scheduler bash
```

## Команды Airflow

```powershell
$compose = "platform/deployment/docker-compose.yml"

# Список обнаруженных DAG-ов
docker compose -f $compose exec airflow-scheduler airflow dags list

# Ошибки импорта DAG-ов
docker compose -f $compose exec airflow-scheduler airflow dags list-import-errors

# Информация о конкретном DAG
docker compose -f $compose exec airflow-scheduler airflow dags details retail_online_retail_ii_landing_ingest_source

# Приостановить / возобновить DAG
docker compose -f $compose exec airflow-scheduler airflow dags pause retail_online_retail_ii_landing_ingest_source
docker compose -f $compose exec airflow-scheduler airflow dags unpause retail_online_retail_ii_landing_ingest_source

# Удалить DAG и связанные с ним метаданные (необратимо)
docker compose -f $compose exec airflow-scheduler airflow dags delete retail_online_retail_ii_landing_ingest_source
```

Команда `airflow dags delete` удаляет связанные с DAG записи из metadata database, включая историю запусков. Используйте её осознанно.

## Данные и volumes

Compose использует постоянные volumes:

- `lakehouse_minio_data` — данные MinIO.
- `lakehouse_postgres_data` — данные PostgreSQL для Iceberg Catalog.
- `lakehouse_airflow_postgres_data` — metadata database Airflow.

Посмотреть volumes:

```powershell
docker volume ls
```

Не удаляйте эти volumes при обычной остановке или пересоздании контейнеров: в них хранятся данные сервисов.

## Структура документации

- [Архитектурные решения (ADR)](architecture/decisions/)
- [ADR 0002 — модель исполнения Airflow](architecture/decisions/0002-airflow-execution-model.md)
