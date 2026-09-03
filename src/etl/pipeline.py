import logging

from .extract import extract_data
from .transform import (
    transform_all,
    create_order_items_fact,
)
from .data_quality import run_quality_checks
from .load import load_parquet


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run_pipeline():
    """
    Execute the complete e-commerce ETL pipeline.
    """

    logger.info("Starting E-Commerce ETL Pipeline")

    # ---------------------------------------------------------
    # 1. EXTRACT
    # ---------------------------------------------------------

    logger.info("Starting EXTRACT stage")

    raw_data = extract_data()

    logger.info(
        "EXTRACT stage completed successfully"
    )

    # ---------------------------------------------------------
    # 2. TRANSFORM
    # ---------------------------------------------------------

    logger.info("Starting TRANSFORM stage")

    transformed_data = transform_all(raw_data)

    fact_table = create_order_items_fact(
        orders=transformed_data["orders"],
        order_items=transformed_data["order_items"],
        products=transformed_data["products"],
        customers=transformed_data["customers"],
        category_translation=transformed_data[
            "category_translation"
        ],
    )

    logger.info(
        "Fact table created: %s rows × %s columns",
        f"{fact_table.shape[0]:,}",
        fact_table.shape[1],
    )

    logger.info(
        "TRANSFORM stage completed successfully"
    )

    # ---------------------------------------------------------
    # 3. DATA QUALITY
    # ---------------------------------------------------------

    logger.info("Starting DATA QUALITY validation")

    quality_passed = run_quality_checks(fact_table)

    if not quality_passed:
        logger.error(
            "Data quality validation failed. "
            "Stopping pipeline."
        )

        raise RuntimeError(
            "ETL pipeline stopped because "
            "data quality validation failed."
        )

    logger.info(
        "DATA QUALITY validation passed"
    )

    # ---------------------------------------------------------
    # 4. LOAD
    # ---------------------------------------------------------

    logger.info("Starting LOAD stage")

    output_path = load_parquet(
        fact_table,
        "order_items_fact.parquet",
    )

    logger.info(
        "LOAD stage completed successfully"
    )

    # ---------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------

    logger.info(
        "ETL Pipeline completed successfully"
    )

    logger.info(
        "Output file: %s",
        output_path,
    )

    logger.info(
        "Rows loaded: %s",
        f"{fact_table.shape[0]:,}",
    )

    logger.info(
        "Columns loaded: %s",
        fact_table.shape[1],
    )


if __name__ == "__main__":
    run_pipeline()