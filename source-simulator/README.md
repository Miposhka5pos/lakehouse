# Source Simulator — Incremental v1

Изолированный PostgreSQL 17 источник для отработки инкрементальной загрузки без CDC и без физического удаления строк.

## Модель

База: `source_db`  
Схема: `source_incremental`

| Таблица | Первичный ключ | Назначение |
|---|---|---|
| customers | customer_id | Клиенты |
| products | product_id | Товары |
| orders | order_id | Заказы |
| order_items | order_item_id | Позиции заказов |

Все таблицы содержат `created_at`, `updated_at` и `is_deleted`. Триггеры PostgreSQL автоматически обновляют `updated_at` при UPDATE. Логическое удаление выполняется через `is_deleted = TRUE`; физический DELETE в этом сценарии не используется.

Поле `orders.country` — снимок страны на момент создания заказа, оно не меняется автоматически при изменении страны клиента. Продажей в аналитических витринах считается заказ со статусом `DELIVERED`; это правило должно применяться в Silver/Gold, а не в генераторе источника.

Инкрементальное чтение выполняется отдельно для каждой таблицы по `updated_at`. Запрос обязан включать строки с `is_deleted = TRUE`, чтобы передать tombstone в Lakehouse. Рекомендуется overlap window и идемпотентный MERGE в Silver.

## Запуск

Сначала создай внешнюю сеть Lakehouse и подними инфраструктуру, в Compose которой объявлена сеть `lakehouse_iceberg_net`.

Из корня репозитория:

```powershell
Copy-Item source-simulator/deployment/.env.example source-simulator/deployment/.env
# Измени POSTGRES_PASSWORD в source-simulator/deployment/.env

docker compose --env-file source-simulator/deployment/.env -f source-simulator/deployment/docker-compose.yml up -d
docker compose --env-file source-simulator/deployment/.env -f source-simulator/deployment/docker-compose.yml ps
```

Данные PostgreSQL сохраняются в отдельном volume `source_simulator_postgres_data`. Не используй `down -v`, если не собираешься намеренно удалять тестовую базу.

Проверка готовности:

```powershell
docker exec source-postgres pg_isready -U source_user -d source_db
```

Доступ из контейнеров в сети Lakehouse:

```text
host: source-postgres
port: 5432
database: source_db
schema: source_incremental
JDBC: jdbc:postgresql://source-postgres:5432/source_db
```

С хоста PostgreSQL доступен на `localhost:5433` по умолчанию.

## Генерация данных

Установи зависимости локально или запускай генератор в Python-контейнере. Пример для локального Python:

```powershell
py -m venv source-simulator/.venv
source-simulator/.venv/Scripts/Activate.ps1
pip install -r source-simulator/simulator/requirements.txt

$env:PGHOST = "localhost"
$env:PGPORT = "5433"
$env:PGDATABASE = "source_db"
$env:PGUSER = "source_user"
$env:PGPASSWORD = "значение из deployment/.env"

python source-simulator/simulator/generate_data.py seed
```

По умолчанию создаются 500 клиентов, 200 товаров, 5 000 заказов и примерно 10 000–20 000 позиций. Один и тот же seed даёт одинаковые значения и идентификаторы. Повторный запуск не дублирует строки с теми же первичными ключами; он не очищает и не перезаписывает существующие данные.

Настройка объёма:

```powershell
python source-simulator/simulator/generate_data.py seed --customers 500 --products 200 --orders 5000 --seed 42
```

Добавить новые заказы и позиции:

```powershell
python source-simulator/simulator/generate_data.py insert-orders --count 20
```

Сымитировать изменения, логические удаления и восстановления:

```powershell
python source-simulator/simulator/generate_data.py mutate --count 25
```

Каждый UPDATE автоматически меняет `updated_at`. Генератор не выполняет физический DELETE.

## Проверка таблиц

```sql
SELECT 'customers' AS table_name, COUNT(*) FROM source_incremental.customers
UNION ALL SELECT 'products', COUNT(*) FROM source_incremental.products
UNION ALL SELECT 'orders', COUNT(*) FROM source_incremental.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM source_incremental.order_items;

SELECT status, COUNT(*)
FROM source_incremental.orders
GROUP BY status
ORDER BY status;

SELECT
    COUNT(*) FILTER (WHERE is_deleted) AS soft_deleted,
    COUNT(*) FILTER (WHERE NOT is_deleted) AS active
FROM source_incremental.orders;
```

## Границы сценария

- Нет CDC, transaction log capture или хранения всех промежуточных версий.
- Если строка изменится несколько раз между опросами, источник отдаст только её последнее состояние.
- Нет сценария физического DELETE.
- Для каждой таблицы нужен собственный checkpoint: изменение позиции заказа не обязано обновлять строку заказа.
- `updated_at` — время изменения строки в источнике; для промышленной гарантии против поздних commit требуется дополнительная стратегия согласованного чтения и периодической сверки.
