# Airflow: local setup

This folder runs Apache Airflow locally and connects it to the existing e-commerce ETL code.

## First-time setup

From this folder, run:

```bash
docker compose --profile init up airflow-init
docker compose up -d
```

Then open <http://localhost:8080> and sign in with `airflow` / `airflow`.

## What the DAG does today

`ecommerce_data_pipeline` first calls the existing `src.etl.pipeline.run_pipeline` function. That function extracts the raw CSV files, transforms and validates the data, then saves `data/processed/order_items_fact.parquet`.

After the ETL task succeeds, Airflow runs the existing `src.warehouse.loader.load_warehouse` function. It upserts the Parquet output into the local PostgreSQL warehouse, so re-running the DAG does not create duplicate warehouse records.

## Stop it

```bash
docker compose down
```
