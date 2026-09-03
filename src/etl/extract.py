from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data/raw")


def extract_data() -> dict[str, pd.DataFrame]:
    """
    Extract all raw Olist datasets into pandas DataFrames.
    """

    datasets = {
        "customers": "olist_customers_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "order_payments": "olist_order_payments_dataset.csv",
        "order_reviews": "olist_order_reviews_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }

    data = {}

    for name, filename in datasets.items():
        file_path = RAW_DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Raw dataset not found: {file_path}"
            )

        data[name] = pd.read_csv(file_path)

        print(
            f"Extracted {name}: "
            f"{data[name].shape[0]:,} rows, "
            f"{data[name].shape[1]} columns"
        )

    return data

