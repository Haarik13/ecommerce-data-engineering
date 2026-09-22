"""Orchestrate the existing e-commerce ETL pipeline."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from src.etl.pipeline import run_pipeline
from src.warehouse.loader import load_warehouse


def run_warehouse_load() -> dict[str, int]:
    """Load the validated Parquet output into the PostgreSQL warehouse."""
    return load_warehouse().as_dict()


with DAG(
    dag_id="ecommerce_data_pipeline",
    description="Runs the existing e-commerce ETL pipeline.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ecommerce", "etl"],
    default_args={
        # Retry temporary failures twice before marking a task as failed.
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
) as dag:
    run_etl_pipeline = PythonOperator(
        task_id="run_etl_pipeline",
        python_callable=run_pipeline,
    )

    load_to_warehouse = PythonOperator(
        task_id="load_to_warehouse",
        python_callable=run_warehouse_load,
    )

    run_etl_pipeline >> load_to_warehouse
