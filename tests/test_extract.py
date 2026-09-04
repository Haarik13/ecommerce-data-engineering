import pandas as pd

from src.etl.extract import extract_data


def test_extract_data_returns_all_datasets():
    data = extract_data()

    expected_datasets = {
        "customers",
        "geolocation",
        "order_items",
        "order_payments",
        "order_reviews",
        "orders",
        "products",
        "sellers",
        "category_translation",
    }

    assert set(data.keys()) == expected_datasets


def test_extract_data_returns_dataframes():
    data = extract_data()

    for name, df in data.items():
        assert isinstance(df, pd.DataFrame), (
            f"{name} is not a pandas DataFrame"
        )


def test_extract_data_expected_row_counts():
    data = extract_data()

    expected_row_counts = {
        "customers": 99_441,
        "geolocation": 1_000_163,
        "order_items": 112_650,
        "order_payments": 103_886,
        "order_reviews": 99_224,
        "orders": 99_441,
        "products": 32_951,
        "sellers": 3_095,
        "category_translation": 71,
    }

    for name, expected_count in expected_row_counts.items():
        assert len(data[name]) == expected_count, (
            f"{name}: expected {expected_count:,} rows, "
            f"got {len(data[name]):,}"
        )