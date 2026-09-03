from pathlib import Path

import pandas as pd


PROCESSED_DATA_DIR = Path("data/processed")


def load_parquet(
    df: pd.DataFrame,
    filename: str,
) -> Path:
    """
    Save a DataFrame as a compressed Parquet file.
    """

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = PROCESSED_DATA_DIR / filename

    df.to_parquet(
        output_path,
        index=False,
        compression="snappy",
    )

    print(
        f"Loaded {len(df):,} rows into "
        f"{output_path}"
    )

    return output_path

