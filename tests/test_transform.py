import pandas as pd

from src.etl.extract import extract_data
from src.etl.transform import (
    transform_all,
    create_order_items_fact,
)


def test_transform_all_preserves_datasets():
    raw_data = extract_data()
    transformed_data = transform_all(raw_data)

    assert set(transformed_data.keys()) == set(raw_data.keys())

    for name in raw_data:
        assert isinstance(transformed_data[name], pd.DataFrame)


def test_orders_timestamps_are_datetime():
    raw_data = extract_data()
    transformed_data = transform_all(raw_data)

    orders = transformed_data["orders"]

    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in timestamp_columns:
        assert pd.api.types.is_datetime64_any_dtype(
            orders[column]
        )


def test_order_items_numeric_columns():
    raw_data = extract_data()
    transformed_data = transform_all(raw_data)

    order_items = transformed_data["order_items"]

    numeric_columns = [
        "order_item_id",
        "price",
        "freight_value",
    ]

    for column in numeric_columns:
        assert pd.api.types.is_numeric_dtype(
            order_items[column]
        )


def test_create_order_items_fact_table():
    raw_data = extract_data()
    transformed_data = transform_all(raw_data)

    fact = create_order_items_fact(
        orders=transformed_data["orders"],
        order_items=transformed_data["order_items"],
        products=transformed_data["products"],
        customers=transformed_data["customers"],
        category_translation=transformed_data[
            "category_translation"
        ],
    )

    assert isinstance(fact, pd.DataFrame)

    assert fact.shape == (112_650, 26)

    required_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "customer_id",
        "customer_unique_id",
        "product_category_name",
        "product_category_name_english",
        "price",
        "freight_value",
        "item_total_value",
        "delivery_days",
        "is_late_delivery",
    ]

    for column in required_columns:
        assert column in fact.columns


def test_item_total_value_calculation():
    raw_data = extract_data()
    transformed_data = transform_all(raw_data)

    fact = create_order_items_fact(
        orders=transformed_data["orders"],
        order_items=transformed_data["order_items"],
        products=transformed_data["products"],
        customers=transformed_data["customers"],
        category_translation=transformed_data[
            "category_translation"
        ],
    )

    expected_total = (
        fact["price"] + fact["freight_value"]
    )

    pd.testing.assert_series_equal(
        fact["item_total_value"],
        expected_total,
        check_names=False,
    )


def test_delivery_days_are_non_negative():
    raw_data = extract_data()
    transformed_data = transform_all(raw_data)

    fact = create_order_items_fact(
        orders=transformed_data["orders"],
        order_items=transformed_data["order_items"],
        products=transformed_data["products"],
        customers=transformed_data["customers"],
        category_translation=transformed_data[
            "category_translation"
        ],
    )

    valid_delivery_days = fact["delivery_days"].dropna()

    assert (valid_delivery_days >= 0).all()