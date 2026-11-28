#!/usr/bin/env python3
"""Generate deterministic synthetic retail data and incremental test mutations."""

from __future__ import annotations

import argparse
import os
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Iterable

import psycopg
from faker import Faker
from psycopg.rows import dict_row

SCHEMA = "source_incremental"
COUNTRIES = [
    "Finland", "Germany", "France", "United Kingdom", "Spain",
    "Italy", "Netherlands", "Sweden", "Poland", "United States",
]
CATEGORIES = [
    "Electronics", "Home", "Kitchen", "Books", "Clothing", "Sports",
    "Beauty", "Toys", "Garden", "Automotive", "Office", "Grocery",
]
STATUSES = ["NEW", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5433")),
        dbname=os.getenv("PGDATABASE", "source_db"),
        user=os.getenv("PGUSER", "source_user"),
        password=os.environ["PGPASSWORD"],
        row_factory=dict_row,
    )


def chunks(items: Iterable, size: int = 1000):
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def seed_data(conn, customer_count: int, product_count: int, order_count: int, seed: int):
    rng = random.Random(seed)
    fake = Faker("en_US")
    fake.seed_instance(seed)
    base_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

    customers = []
    for customer_id in range(1, customer_count + 1):
        customers.append((
            customer_id, fake.name(), f"customer{customer_id}@example.test",
            rng.choice(COUNTRIES), base_time + timedelta(days=rng.randrange(730)),
        ))
    conn.executemany(
        f"""INSERT INTO {SCHEMA}.customers
            (customer_id, customer_name, email, country, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO NOTHING""",
        customers,
    )

    products = []
    for product_id in range(1, product_count + 1):
        products.append((
            product_id, fake.catch_phrase()[:200], rng.choice(CATEGORIES),
            rng.choice(["piece", "kg", "pack", "liter"]),
            base_time + timedelta(days=rng.randrange(730)),
        ))
    conn.executemany(
        f"""INSERT INTO {SCHEMA}.products
            (product_id, product_name, category, unit_of_measure, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO NOTHING""",
        products,
    )

    customer_country = {row[0]: row[3] for row in customers}
    orders = []
    item_rows = []
    next_item_id = 1
    for order_id in range(1, order_count + 1):
        customer_id = rng.randint(1, customer_count)
        order_time = base_time + timedelta(
            days=rng.randrange(730), seconds=rng.randrange(86400)
        )
        status = rng.choices(
            STATUSES, weights=[8, 8, 8, 12, 58, 6], k=1
        )[0]
        orders.append((
            order_id, customer_id, order_time, status,
            customer_country[customer_id], order_time,
        ))
        for product_id in rng.sample(
            range(1, product_count + 1),
            k=rng.randint(1, min(4, product_count)),
        ):
            quantity = rng.randint(1, 10)
            price = Decimal(rng.randint(100, 50000)) / Decimal("100")
            item_rows.append((
                next_item_id, order_id, product_id, quantity, price, order_time,
            ))
            next_item_id += 1

    conn.executemany(
        f"""INSERT INTO {SCHEMA}.orders
            (order_id, customer_id, order_date, status, country, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING""",
        orders,
    )
    for batch in chunks(item_rows):
        conn.executemany(
            f"""INSERT INTO {SCHEMA}.order_items
                (order_item_id, order_id, product_id, quantity, unit_price, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_item_id) DO NOTHING""",
            batch,
        )

    # Explicit deterministic IDs are used above; advance identity sequences so
    # later inserts that omit IDs do not collide with the seeded records.
    for table, column in (
        ("customers", "customer_id"),
        ("products", "product_id"),
        ("orders", "order_id"),
        ("order_items", "order_item_id"),
    ):
        conn.execute(
            f"""SELECT setval(
                pg_get_serial_sequence('{SCHEMA}.{table}', '{column}'),
                GREATEST(COALESCE((SELECT MAX({column}) FROM {SCHEMA}.{table}), 1), 1),
                EXISTS (SELECT 1 FROM {SCHEMA}.{table})
            )"""
        )

    conn.commit()
    counts = {}
    for table in ("customers", "products", "orders", "order_items"):
        row = conn.execute(f"SELECT COUNT(*) AS n FROM {SCHEMA}.{table}").fetchone()
        counts[table] = row["n"]
    return counts


def insert_orders(conn, count: int, seed: int):
    rng = random.Random(seed)
    customers = conn.execute(
        f"SELECT customer_id, country FROM {SCHEMA}.customers WHERE NOT is_deleted"
    ).fetchall()
    products = conn.execute(
        f"SELECT product_id FROM {SCHEMA}.products WHERE NOT is_deleted"
    ).fetchall()
    if not customers or not products:
        raise RuntimeError("Seed customers and products before inserting orders.")

    for _ in range(count):
        customer = rng.choice(customers)
        order_time = datetime.now(timezone.utc)
        status = rng.choice(STATUSES)
        order = conn.execute(
            f"""INSERT INTO {SCHEMA}.orders
                (customer_id, order_date, status, country)
                VALUES (%s, %s, %s, %s)
                RETURNING order_id""",
            (customer["customer_id"], order_time, status, customer["country"]),
        ).fetchone()
        selected_products = rng.sample(products, k=min(len(products), rng.randint(1, 3)))
        for product in selected_products:
            conn.execute(
                f"""INSERT INTO {SCHEMA}.order_items
                    (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)""",
                (
                    order["order_id"], product["product_id"], rng.randint(1, 8),
                    Decimal(rng.randint(100, 30000)) / Decimal("100"),
                ),
            )
    conn.commit()
    return count


def mutate_data(conn, count: int, seed: int):
    rng = random.Random(seed)
    actions = ("update_customer", "update_order", "update_item", "soft_delete", "restore")
    completed = {name: 0 for name in actions}

    for _ in range(count):
        action = rng.choice(actions)
        if action == "update_customer":
            row = conn.execute(
                f"SELECT customer_id FROM {SCHEMA}.customers WHERE NOT is_deleted ORDER BY random() LIMIT 1"
            ).fetchone()
            if row:
                conn.execute(
                    f"UPDATE {SCHEMA}.customers SET country = %s WHERE customer_id = %s",
                    (rng.choice(COUNTRIES), row["customer_id"]),
                )
        elif action == "update_order":
            row = conn.execute(
                f"SELECT order_id, status FROM {SCHEMA}.orders WHERE NOT is_deleted ORDER BY random() LIMIT 1"
            ).fetchone()
            if row:
                choices = [status for status in STATUSES if status != row["status"]]
                conn.execute(
                    f"UPDATE {SCHEMA}.orders SET status = %s WHERE order_id = %s",
                    (rng.choice(choices), row["order_id"]),
                )
        elif action == "update_item":
            row = conn.execute(
                f"SELECT order_item_id FROM {SCHEMA}.order_items WHERE NOT is_deleted ORDER BY random() LIMIT 1"
            ).fetchone()
            if row:
                conn.execute(
                    f"""UPDATE {SCHEMA}.order_items
                        SET quantity = %s, unit_price = %s
                        WHERE order_item_id = %s""",
                    (
                        rng.randint(1, 12),
                        Decimal(rng.randint(100, 50000)) / Decimal("100"),
                        row["order_item_id"],
                    ),
                )
        elif action == "soft_delete":
            table, key = rng.choice((
                ("customers", "customer_id"), ("products", "product_id"),
                ("orders", "order_id"), ("order_items", "order_item_id"),
            ))
            row = conn.execute(
                f"SELECT {key} AS id FROM {SCHEMA}.{table} WHERE NOT is_deleted ORDER BY random() LIMIT 1"
            ).fetchone()
            if row:
                conn.execute(
                    f"UPDATE {SCHEMA}.{table} SET is_deleted = TRUE WHERE {key} = %s",
                    (row["id"],),
                )
        else:
            table, key = rng.choice((
                ("customers", "customer_id"), ("products", "product_id"),
                ("orders", "order_id"), ("order_items", "order_item_id"),
            ))
            row = conn.execute(
                f"SELECT {key} AS id FROM {SCHEMA}.{table} WHERE is_deleted ORDER BY random() LIMIT 1"
            ).fetchone()
            if row:
                conn.execute(
                    f"UPDATE {SCHEMA}.{table} SET is_deleted = FALSE WHERE {key} = %s",
                    (row["id"],),
                )
        if row:
            completed[action] += 1

    conn.commit()
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed", help="Insert the initial deterministic dataset.")
    seed_parser.add_argument("--customers", type=int, default=500)
    seed_parser.add_argument("--products", type=int, default=200)
    seed_parser.add_argument("--orders", type=int, default=5000)
    seed_parser.add_argument("--seed", type=int, default=42)

    insert_parser = subparsers.add_parser("insert-orders", help="Insert new orders and order items.")
    insert_parser.add_argument("--count", type=int, default=20)
    insert_parser.add_argument("--seed", type=int, default=101)

    mutate_parser = subparsers.add_parser("mutate", help="Update and soft-delete/restore existing rows.")
    mutate_parser.add_argument("--count", type=int, default=25)
    mutate_parser.add_argument("--seed", type=int, default=202)

    args = parser.parse_args()
    if args.command == "seed" and min(args.customers, args.products, args.orders) < 1:
        parser.error("customers, products and orders must all be positive")
    if args.command != "seed" and args.count < 1:
        parser.error("count must be positive")

    with connect() as conn:
        if args.command == "seed":
            result = seed_data(conn, args.customers, args.products, args.orders, args.seed)
            print("Current table counts:", result)
        elif args.command == "insert-orders":
            print(f"Inserted orders: {insert_orders(conn, args.count, args.seed)}")
        else:
            print("Applied mutations:", mutate_data(conn, args.count, args.seed))


if __name__ == "__main__":
    main()
