import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform generic cleaning operations on a DataFrame.
    """

    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove duplicate rows
    df = df.drop_duplicates()

    return df


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean customer data.
    """

    df = clean_dataframe(df)

    return df


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean orders and convert timestamp columns to datetime.
    """

    df = clean_dataframe(df)

    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in timestamp_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean order item data.
    """

    df = clean_dataframe(df)

    numeric_columns = [
        "order_item_id",
        "price",
        "freight_value",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def transform_order_payments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean payment data.
    """

    df = clean_dataframe(df)

    numeric_columns = [
        "payment_sequential",
        "payment_installments",
        "payment_value",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def transform_order_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean review data.
    """

    df = clean_dataframe(df)

    if "review_score" in df.columns:
        df["review_score"] = pd.to_numeric(
            df["review_score"],
            errors="coerce"
        )

    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean product data.
    """

    df = clean_dataframe(df)

    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def transform_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean seller data.
    """

    df = clean_dataframe(df)

    return df


def transform_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean geolocation data.
    """

    df = clean_dataframe(df)

    return df


def transform_category_translation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean product category translation data.
    """

    df = clean_dataframe(df)

    return df


def transform_all(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Apply dataset-specific transformations to all extracted datasets.
    """

    transformed = {
        "customers": transform_customers(data["customers"]),
        "orders": transform_orders(data["orders"]),
        "order_items": transform_order_items(data["order_items"]),
        "order_payments": transform_order_payments(data["order_payments"]),
        "order_reviews": transform_order_reviews(data["order_reviews"]),
        "products": transform_products(data["products"]),
        "sellers": transform_sellers(data["sellers"]),
        "geolocation": transform_geolocation(data["geolocation"]),
        "category_translation": transform_category_translation(
            data["category_translation"]
        ),
    }

    return transformed

def create_order_items_fact(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
    category_translation: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create an analytics-ready order-item fact table.
    """

    # Join order items with orders
    fact = order_items.merge(
        orders[
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ]
        ],
        on="order_id",
        how="left",
    )

    # Join customer information
    fact = fact.merge(
        customers[
            [
                "customer_id",
                "customer_unique_id",
                "customer_city",
                "customer_state",
            ]
        ],
        on="customer_id",
        how="left",
    )

    # Join product information
    fact = fact.merge(
        products[
            [
                "product_id",
                "product_category_name",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ]
        ],
        on="product_id",
        how="left",
    )

    # Join English category names
    fact = fact.merge(
        category_translation,
        on="product_category_name",
        how="left",
    )

    # Calculate total item value
    fact["item_total_value"] = (
        fact["price"] + fact["freight_value"]
    )

    # Calculate delivery duration
    fact["delivery_days"] = (
        fact["order_delivered_customer_date"]
        - fact["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    # Calculate whether delivery was late
    fact["is_late_delivery"] = (
        fact["order_delivered_customer_date"]
        > fact["order_estimated_delivery_date"]
    )

    return fact

