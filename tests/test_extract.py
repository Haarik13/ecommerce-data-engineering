from pathlib import Path

import pandas as pd

from src.etl.extract import extract_data


TEST_DATA_DIR = Path(__file__).parent / "fixtures"


def test_extract_data_returns_all_datasets():
    data = extract_data(data_dir=TEST_DATA_DIR)

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
    data = extract_data(data_dir=TEST_DATA_DIR)

    for name, df in data.items():
        assert isinstance(df, pd.DataFrame), (
            f"{name} is not a pandas DataFrame"
        )


def test_extract_data_expected_row_counts():
    data = extract_data(data_dir=TEST_DATA_DIR)

    expected_row_counts = {
        "customers": 2,
        "geolocation": 2,
        "order_items": 3,
        "order_payments": 2,
        "order_reviews": 2,
        "orders": 2,
        "products": 2,
        "sellers": 2,
        "category_translation": 2,
    }

    for name, expected_count in expected_row_counts.items():
        assert len(data[name]) == expected_count, (
            f"{name}: expected {expected_count:,} rows, "
            f"got {len(data[name]):,}"
        )