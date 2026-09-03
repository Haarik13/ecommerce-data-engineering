import pandas as pd


def check_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> bool:
    """
    Check that all required columns exist.
    """

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(
            f"FAIL: Missing columns: {missing_columns}"
        )
        return False

    print("PASS: Required columns are present.")
    return True


def check_duplicate_order_items(df: pd.DataFrame) -> bool:
    """
    Check for duplicate order_id + order_item_id combinations.
    """

    duplicates = df.duplicated(
        subset=["order_id", "order_item_id"]
    ).sum()

    if duplicates > 0:
        print(
            f"FAIL: Found {duplicates:,} duplicate "
            "order-item records."
        )
        return False

    print("PASS: No duplicate order-item records.")
    return True


def check_nulls(
    df: pd.DataFrame,
    critical_columns: list[str],
) -> bool:
    """
    Check for null values in critical columns.
    """

    null_counts = df[critical_columns].isnull().sum()
    null_counts = null_counts[null_counts > 0]

    if not null_counts.empty:
        print("FAIL: Null values found:")
        print(null_counts)
        return False

    print("PASS: No nulls in critical columns.")
    return True


def check_numeric_values(df: pd.DataFrame) -> bool:
    """
    Check that monetary values are not negative.
    """

    invalid_price = (df["price"] < 0).sum()
    invalid_freight = (df["freight_value"] < 0).sum()
    invalid_total = (df["item_total_value"] < 0).sum()

    if invalid_price > 0:
        print(
            f"FAIL: Found {invalid_price:,} negative prices."
        )
        return False

    if invalid_freight > 0:
        print(
            f"FAIL: Found {invalid_freight:,} negative "
            "freight values."
        )
        return False

    if invalid_total > 0:
        print(
            f"FAIL: Found {invalid_total:,} negative "
            "item totals."
        )
        return False

    print("PASS: Monetary values are valid.")
    return True


def check_review_scores(df: pd.DataFrame) -> bool:
    """
    Check that review scores are between 1 and 5 when present.
    """

    if "review_score" not in df.columns:
        print(
            "SKIP: review_score is not present in this fact table."
        )
        return True

    invalid_scores = (
        df["review_score"].notna()
        & ~df["review_score"].between(1, 5)
    ).sum()

    if invalid_scores > 0:
        print(
            f"FAIL: Found {invalid_scores:,} invalid "
            "review scores."
        )
        return False

    print("PASS: Review scores are valid.")
    return True


def check_delivery_days(df: pd.DataFrame) -> bool:
    """
    Check that delivery duration is not negative.
    """

    invalid_delivery = (
        df["delivery_days"].notna()
        & (df["delivery_days"] < 0)
    ).sum()

    if invalid_delivery > 0:
        print(
            f"FAIL: Found {invalid_delivery:,} "
            "negative delivery durations."
        )
        return False

    print("PASS: Delivery durations are valid.")
    return True


def run_quality_checks(df: pd.DataFrame) -> bool:
    """
    Run all data-quality checks.
    """

    print("\n" + "=" * 60)
    print("DATA QUALITY VALIDATION")
    print("=" * 60)

    required_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "customer_id",
        "price",
        "freight_value",
        "item_total_value",
        "order_purchase_timestamp",
    ]

    critical_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "customer_id",
        "price",
        "freight_value",
    ]

    checks = [
        check_required_columns(
            df,
            required_columns,
        ),
        check_duplicate_order_items(df),
        check_nulls(
            df,
            critical_columns,
        ),
        check_numeric_values(df),
        check_review_scores(df),
        check_delivery_days(df),
    ]

    passed = all(checks)

    print("\n" + "=" * 60)

    if passed:
        print("DATA QUALITY RESULT: PASSED")
    else:
        print("DATA QUALITY RESULT: FAILED")

    print("=" * 60)

    return passed