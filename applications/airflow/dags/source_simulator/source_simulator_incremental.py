from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

import pendulum
import psycopg2

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator


CONNECTION_ID = "source_postgres"
SCHEMA = "source_incremental"

COUNTRIES = [
    "Finland", "Germany", "France", "United Kingdom",
    "Spain", "Italy", "Netherlands", "Sweden",
    "Poland", "United States",
]

STATUSES = [
    "NEW", "CONFIRMED", "PROCESSING",
    "SHIPPED", "DELIVERED", "CANCELLED",
]

TABLES = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
}


def get_connection():
    """Connect using credentials stored in Airflow Connection."""
    airflow_conn = BaseHook.get_connection(CONNECTION_ID)

    return psycopg2.connect(
        host=airflow_conn.host,
        port=airflow_conn.port or 5432,
        dbname=airflow_conn.schema,
        user=airflow_conn.login,
        password=airflow_conn.password,
        connect_timeout=10,
    )


def simulate_source_cycle(**context):
    run_id = context["run_id"]
    rng = random.Random(run_id)

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:

                # 1. Verify schema and source tables.
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    """,
                    (SCHEMA,),
                )

                existing_tables = {
                    row[0] for row in cur.fetchall()
                }

                missing = set(TABLES) - existing_tables

                if missing:
                    raise RuntimeError(
                        f"Missing source tables: {sorted(missing)}"
                    )

                print(
                    f"Connected to source database. "
                    f"Schema {SCHEMA} is available."
                )

                # 2. Load active customers and products.
                cur.execute(
                    f"""
                    SELECT customer_id, country
                    FROM {SCHEMA}.customers
                    WHERE NOT is_deleted
                    """
                )
                customers = cur.fetchall()

                cur.execute(
                    f"""
                    SELECT product_id
                    FROM {SCHEMA}.products
                    WHERE NOT is_deleted
                    """
                )
                products = cur.fetchall()

                if not customers or not products:
                    raise RuntimeError(
                        "Source has no active customers or products. "
                        "Run the initial seed first."
                    )

                # 3. Insert new orders and order items.
                inserted_orders = 3
                inserted_items = 0

                for _ in range(inserted_orders):
                    customer_id, country = rng.choice(customers)

                    cur.execute(
                        f"""
                        INSERT INTO {SCHEMA}.orders
                            (customer_id, order_date, status, country)
                        VALUES (%s, NOW(), %s, %s)
                        RETURNING order_id
                        """,
                        (
                            customer_id,
                            rng.choice(STATUSES),
                            country,
                        ),
                    )

                    order_id = cur.fetchone()[0]

                    selected_products = rng.sample(
                        products,
                        k=min(len(products), rng.randint(1, 3)),
                    )

                    for (product_id,) in selected_products:
                        cur.execute(
                            f"""
                            INSERT INTO {SCHEMA}.order_items
                                (order_id, product_id, quantity, unit_price)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                order_id,
                                product_id,
                                rng.randint(1, 8),
                                Decimal(rng.randint(100, 30000))
                                / Decimal("100"),
                            ),
                        )
                        inserted_items += 1

                # 4. Update existing source records.
                mutations = {
                    "customer_updates": 0,
                    "order_updates": 0,
                    "item_updates": 0,
                    "soft_deletes": 0,
                    "restores": 0,
                }

                cur.execute(
                    f"""
                    SELECT customer_id
                    FROM {SCHEMA}.customers
                    WHERE NOT is_deleted
                    ORDER BY random()
                    LIMIT 3
                    """
                )

                for (customer_id,) in cur.fetchall():
                    cur.execute(
                        f"""
                        UPDATE {SCHEMA}.customers
                        SET country = %s
                        WHERE customer_id = %s
                        """,
                        (rng.choice(COUNTRIES), customer_id),
                    )
                    mutations["customer_updates"] += 1

                cur.execute(
                    f"""
                    SELECT order_id, status
                    FROM {SCHEMA}.orders
                    WHERE NOT is_deleted
                    ORDER BY random()
                    LIMIT 3
                    """
                )

                for order_id, old_status in cur.fetchall():
                    new_status = rng.choice(
                        [s for s in STATUSES if s != old_status]
                    )

                    cur.execute(
                        f"""
                        UPDATE {SCHEMA}.orders
                        SET status = %s
                        WHERE order_id = %s
                        """,
                        (new_status, order_id),
                    )
                    mutations["order_updates"] += 1

                cur.execute(
                    f"""
                    SELECT order_item_id
                    FROM {SCHEMA}.order_items
                    WHERE NOT is_deleted
                    ORDER BY random()
                    LIMIT 3
                    """
                )

                for (item_id,) in cur.fetchall():
                    cur.execute(
                        f"""
                        UPDATE {SCHEMA}.order_items
                        SET quantity = %s, unit_price = %s
                        WHERE order_item_id = %s
                        """,
                        (
                            rng.randint(1, 12),
                            Decimal(rng.randint(100, 50000))
                            / Decimal("100"),
                            item_id,
                        ),
                    )
                    mutations["item_updates"] += 1

                # 5. Soft delete and restore.
                for _ in range(3):
                    table, key = rng.choice(list(TABLES.items()))

                    cur.execute(
                        f"""
                        SELECT {key}
                        FROM {SCHEMA}.{table}
                        WHERE NOT is_deleted
                        ORDER BY random()
                        LIMIT 1
                        """
                    )
                    row = cur.fetchone()

                    if row:
                        cur.execute(
                            f"""
                            UPDATE {SCHEMA}.{table}
                            SET is_deleted = TRUE
                            WHERE {key} = %s
                            """,
                            (row[0],),
                        )
                        mutations["soft_deletes"] += 1

                for _ in range(2):
                    table, key = rng.choice(list(TABLES.items()))

                    cur.execute(
                        f"""
                        SELECT {key}
                        FROM {SCHEMA}.{table}
                        WHERE is_deleted
                        ORDER BY random()
                        LIMIT 1
                        """
                    )
                    row = cur.fetchone()

                    if row:
                        cur.execute(
                            f"""
                            UPDATE {SCHEMA}.{table}
                            SET is_deleted = FALSE
                            WHERE {key} = %s
                            """,
                            (row[0],),
                        )
                        mutations["restores"] += 1

                # 6. Report current table counts.
                counts = {}

                for table in TABLES:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {SCHEMA}.{table}"
                    )
                    counts[table] = cur.fetchone()[0]

                print("Source simulation completed.")
                print(f"Inserted orders: {inserted_orders}")
                print(f"Inserted order items: {inserted_items}")
                print(f"Mutations: {mutations}")
                print(f"Table counts: {counts}")

    finally:
        conn.close()


with DAG(
    dag_id="source_simulator_incremental",
    description="Simulate incremental changes in the PostgreSQL source.",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule="*/15 * * * *",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-platform",
        "retries": 0,
    },
    tags=["source-simulator", "incremental"],
) as dag:

    simulate = PythonOperator(
        task_id="simulate_source_cycle",
        python_callable=simulate_source_cycle,
    )