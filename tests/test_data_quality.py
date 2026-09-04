import pandas as pd

from src.etl.extract import extract_data
from src.etl.transform import (
    transform_all,
    create_order_items_fact,
)
from src.etl.data_quality import run_quality_checks


def build_fact_table():
    raw_data = extract_data()
    transformed_data = transform_all(raw_data)

    return create_order_items_fact(
        orders=transformed_data["orders"],
        order_items=transformed_data["order_items"],
        products=transformed_data["products"],
        customers=transformed_data["customers"],
        category_translation=transformed_data[
            "category_translation"
        ],
    )


def test_data_quality_passes_for_valid_fact_table():
    fact = build_fact_table()

    assert run_quality_checks(fact) is True


def test_fact_table_has_no_duplicate_order_items():
    fact = build_fact_table()

    duplicate_count = fact.duplicated(
        subset=["order_id", "order_item_id"]
    ).sum()

    assert duplicate_count == 0


def test_critical_columns_have_no_nulls():
    fact = build_fact_table()

    critical_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "customer_id",
        "price",
        "freight_value",
    ]

    for column in critical_columns:
        assert fact[column].isna().sum() == 0


def test_monetary_values_are_valid():
    fact = build_fact_table()

    assert (fact["price"] >= 0).all()
    assert (fact["freight_value"] >= 0).all()
    assert (fact["item_total_value"] >= 0).all()


def test_delivery_days_are_valid():
    fact = build_fact_table()

    delivery_days = fact["delivery_days"].dropna()

    assert (delivery_days >= 0).all()