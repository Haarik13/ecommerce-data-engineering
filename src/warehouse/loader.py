"""Load the transformed Olist data into the PostgreSQL star schema.

The loader deliberately keeps the processed Parquet file as the source of
fact-level measures, while reading the raw dimension files for attributes
that are not retained in that file (for example seller location).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


DEFAULT_FACT_PATH = Path("data/processed/order_items_fact.parquet")
DEFAULT_CUSTOMERS_PATH = Path("data/raw/olist_customers_dataset.csv")
DEFAULT_PRODUCTS_PATH = Path("data/raw/olist_products_dataset.csv")
DEFAULT_SELLERS_PATH = Path("data/raw/olist_sellers_dataset.csv")

CHUNK_SIZE = 1_000


@dataclass(frozen=True)
class WarehouseLoadSummary:
    """The number of source records loaded into each warehouse table."""

    customers: int
    products: int
    sellers: int
    dates: int
    order_items: int

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


def _require_columns(
    frame: pd.DataFrame, columns: Iterable[str], source_name: str
) -> None:
    missing = set(columns) - set(frame.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"{source_name} is missing required columns: {missing_columns}")


def _records(frame: pd.DataFrame) -> list[dict[str, object]]:
    """Convert a frame to DBAPI-friendly records, replacing pandas nulls."""
    records: list[dict[str, object]] = []
    for record in frame.to_dict(orient="records"):
        records.append(
            {
                key: None if pd.isna(value) else value
                for key, value in record.items()
            }
        )
    return records


def _chunks(records: list[dict[str, object]]) -> Iterable[list[dict[str, object]]]:
    for start in range(0, len(records), CHUNK_SIZE):
        yield records[start : start + CHUNK_SIZE]


def _upsert(connection, statement: str, frame: pd.DataFrame) -> None:
    records = _records(frame)
    for batch in _chunks(records):
        connection.execute(text(statement), batch)


def _prepare_customers(path: Path) -> pd.DataFrame:
    customers = pd.read_csv(path)
    columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]
    _require_columns(customers, columns, "Customer CSV")
    return customers[columns].drop_duplicates("customer_id")


def _prepare_products(path: Path) -> pd.DataFrame:
    products = pd.read_csv(path).rename(
        columns={
            "product_category_name": "product_category",
            "product_name_lenght": "product_name_length",
            "product_description_lenght": "product_description_length",
        }
    )
    columns = [
        "product_id",
        "product_category",
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    _require_columns(products, columns, "Product CSV")
    return products[columns].drop_duplicates("product_id")


def _prepare_sellers(path: Path) -> pd.DataFrame:
    sellers = pd.read_csv(path)
    columns = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]
    _require_columns(sellers, columns, "Seller CSV")
    return sellers[columns].drop_duplicates("seller_id")


def _prepare_dates(fact: pd.DataFrame) -> pd.DataFrame:
    _require_columns(fact, ["order_purchase_timestamp"], "Fact Parquet")
    dates = pd.to_datetime(fact["order_purchase_timestamp"], errors="coerce").dt.normalize()
    if dates.isna().any():
        raise ValueError("Fact Parquet contains invalid order_purchase_timestamp values.")

    unique_dates = pd.Series(dates.drop_duplicates().sort_values().to_numpy())
    return pd.DataFrame(
        {
            "date_key": unique_dates.dt.strftime("%Y%m%d").astype(int),
            "date": unique_dates.dt.date,
            "year": unique_dates.dt.year,
            "quarter": unique_dates.dt.quarter,
            "month": unique_dates.dt.month,
            "month_name": unique_dates.dt.month_name(),
            "day": unique_dates.dt.day,
            "day_of_week": unique_dates.dt.isocalendar().day.astype(int),
            "day_name": unique_dates.dt.day_name(),
        }
    )


def _read_key_map(connection, table: str, business_key: str, surrogate_key: str) -> dict[str, int]:
    rows = connection.execute(
        text(f"SELECT {business_key}, {surrogate_key} FROM ecommerce.{table}")
    ).mappings()
    return {row[business_key]: row[surrogate_key] for row in rows}


def _prepare_facts(fact: pd.DataFrame, connection) -> pd.DataFrame:
    columns = [
        "order_id",
        "order_item_id",
        "customer_id",
        "product_id",
        "seller_id",
        "order_purchase_timestamp",
        "price",
        "freight_value",
        "item_total_value",
        "delivery_days",
        "is_late_delivery",
    ]
    _require_columns(fact, columns, "Fact Parquet")

    prepared = fact[columns].copy()
    prepared["order_date_key"] = pd.to_datetime(
        prepared.pop("order_purchase_timestamp"), errors="coerce"
    ).dt.strftime("%Y%m%d")
    if prepared["order_date_key"].isna().any():
        raise ValueError("Fact Parquet contains invalid order_purchase_timestamp values.")
    prepared["order_date_key"] = prepared["order_date_key"].astype(int)

    prepared["customer_key"] = prepared["customer_id"].map(
        _read_key_map(connection, "dim_customer", "customer_id", "customer_key")
    )
    prepared["product_key"] = prepared["product_id"].map(
        _read_key_map(connection, "dim_product", "product_id", "product_key")
    )
    prepared["seller_key"] = prepared["seller_id"].map(
        _read_key_map(connection, "dim_seller", "seller_id", "seller_key")
    )

    missing_keys = prepared[["customer_key", "product_key", "seller_key"]].isna().any(axis=1)
    if missing_keys.any():
        raise ValueError(
            f"{missing_keys.sum()} fact rows could not be matched to warehouse dimensions."
        )

    prepared["delivery_days"] = pd.to_numeric(
        prepared["delivery_days"], errors="coerce"
    ).round().astype("Int64")
    return prepared[
        [
            "order_id",
            "order_item_id",
            "customer_key",
            "product_key",
            "seller_key",
            "order_date_key",
            "price",
            "freight_value",
            "item_total_value",
            "delivery_days",
            "is_late_delivery",
        ]
    ]


def load_warehouse(
    engine: Engine | None = None,
    fact_path: Path = DEFAULT_FACT_PATH,
    customers_path: Path = DEFAULT_CUSTOMERS_PATH,
    products_path: Path = DEFAULT_PRODUCTS_PATH,
    sellers_path: Path = DEFAULT_SELLERS_PATH,
) -> WarehouseLoadSummary:
    """Upsert dimensions and facts from the pipeline's local data assets.

    Re-running this function is safe: each table is upserted using its
    warehouse business key rather than adding duplicate records.
    """
    if engine is None:
        # Import lazily so data-preparation helpers remain testable without DB config.
        from .connection import engine as configured_engine

        engine = configured_engine

    fact = pd.read_parquet(fact_path)
    customers = _prepare_customers(customers_path)
    products = _prepare_products(products_path)
    sellers = _prepare_sellers(sellers_path)
    dates = _prepare_dates(fact)

    with engine.begin() as connection:
        _upsert(
            connection,
            """
            INSERT INTO ecommerce.dim_customer
                (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
            VALUES
                (:customer_id, :customer_unique_id, :customer_zip_code_prefix, :customer_city, :customer_state)
            ON CONFLICT (customer_id) DO UPDATE SET
                customer_unique_id = EXCLUDED.customer_unique_id,
                customer_zip_code_prefix = EXCLUDED.customer_zip_code_prefix,
                customer_city = EXCLUDED.customer_city,
                customer_state = EXCLUDED.customer_state
            """,
            customers,
        )
        _upsert(
            connection,
            """
            INSERT INTO ecommerce.dim_product
                (product_id, product_category, product_name_length, product_description_length,
                 product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
            VALUES
                (:product_id, :product_category, :product_name_length, :product_description_length,
                 :product_photos_qty, :product_weight_g, :product_length_cm, :product_height_cm, :product_width_cm)
            ON CONFLICT (product_id) DO UPDATE SET
                product_category = EXCLUDED.product_category,
                product_name_length = EXCLUDED.product_name_length,
                product_description_length = EXCLUDED.product_description_length,
                product_photos_qty = EXCLUDED.product_photos_qty,
                product_weight_g = EXCLUDED.product_weight_g,
                product_length_cm = EXCLUDED.product_length_cm,
                product_height_cm = EXCLUDED.product_height_cm,
                product_width_cm = EXCLUDED.product_width_cm
            """,
            products,
        )
        _upsert(
            connection,
            """
            INSERT INTO ecommerce.dim_seller
                (seller_id, seller_zip_code_prefix, seller_city, seller_state)
            VALUES
                (:seller_id, :seller_zip_code_prefix, :seller_city, :seller_state)
            ON CONFLICT (seller_id) DO UPDATE SET
                seller_zip_code_prefix = EXCLUDED.seller_zip_code_prefix,
                seller_city = EXCLUDED.seller_city,
                seller_state = EXCLUDED.seller_state
            """,
            sellers,
        )
        _upsert(
            connection,
            """
            INSERT INTO ecommerce.dim_date
                (date_key, date, year, quarter, month, month_name, day, day_of_week, day_name)
            VALUES
                (:date_key, :date, :year, :quarter, :month, :month_name, :day, :day_of_week, :day_name)
            ON CONFLICT (date_key) DO UPDATE SET
                date = EXCLUDED.date,
                year = EXCLUDED.year,
                quarter = EXCLUDED.quarter,
                month = EXCLUDED.month,
                month_name = EXCLUDED.month_name,
                day = EXCLUDED.day,
                day_of_week = EXCLUDED.day_of_week,
                day_name = EXCLUDED.day_name
            """,
            dates,
        )
        facts = _prepare_facts(fact, connection)
        _upsert(
            connection,
            """
            INSERT INTO ecommerce.fact_order_items
                (order_id, order_item_id, customer_key, product_key, seller_key, order_date_key,
                 price, freight_value, item_total_value, delivery_days, is_late_delivery)
            VALUES
                (:order_id, :order_item_id, :customer_key, :product_key, :seller_key, :order_date_key,
                 :price, :freight_value, :item_total_value, :delivery_days, :is_late_delivery)
            ON CONFLICT (order_id, order_item_id) DO UPDATE SET
                customer_key = EXCLUDED.customer_key,
                product_key = EXCLUDED.product_key,
                seller_key = EXCLUDED.seller_key,
                order_date_key = EXCLUDED.order_date_key,
                price = EXCLUDED.price,
                freight_value = EXCLUDED.freight_value,
                item_total_value = EXCLUDED.item_total_value,
                delivery_days = EXCLUDED.delivery_days,
                is_late_delivery = EXCLUDED.is_late_delivery
            """,
            facts,
        )

    return WarehouseLoadSummary(
        customers=len(customers),
        products=len(products),
        sellers=len(sellers),
        dates=len(dates),
        order_items=len(facts),
    )


if __name__ == "__main__":
    print(load_warehouse().as_dict())
