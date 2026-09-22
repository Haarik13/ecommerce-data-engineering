# E-Commerce Data Engineering Pipeline

An end-to-end data engineering pipeline built using Python, SQL, PostgreSQL, and Apache Airflow to ingest, transform, validate, warehouse, and orchestrate e-commerce data.

The project uses the Brazilian E-Commerce Public Dataset by Olist and demonstrates a production-style data engineering workflow, including automated testing, CI/CD validation, data transformation, PostgreSQL warehousing, and workflow orchestration.

---

## Project Overview

The pipeline processes multiple raw e-commerce datasets and transforms them into an analytics-ready warehouse.

The project demonstrates the following data engineering concepts:

- Data ingestion and extraction
- Data transformation and cleaning
- Data quality validation
- Fact table creation
- PostgreSQL data warehousing
- Automated testing with pytest
- Continuous Integration with GitHub Actions
- Workflow orchestration with Apache Airflow
- Docker-based development environment
- Git/GitHub version control

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Data ingestion, transformation, validation, and pipeline logic |
| Pandas | Data processing and transformation |
| PostgreSQL | Data warehouse |
| SQL | Warehouse queries and analytics |
| Apache Airflow | Pipeline orchestration |
| Docker | Containerized services |
| Pytest | Automated testing |
| Git/GitHub | Version control |
| GitHub Actions | Continuous Integration |
| PyArrow/Parquet | Processed data storage |

---

## Project Architecture

```text
                    Olist Raw CSV Data
                           |
                           v
                    Data Extraction
                           |
                           v
                  Data Transformation
                           |
                           v
                  Data Quality Checks
                           |
                           v
                 Processed Parquet Data
                           |
                           v
                  PostgreSQL Warehouse
                           |
                           v
                  Analytics / SQL Queries


             Apache Airflow
                    |
                    v
          ┌─────────────────────┐
          │     ETL Pipeline    │
          └─────────────────────┘
                    |
                    v
          ┌─────────────────────┐
          │ Warehouse Loading   │
          └─────────────────────┘
```

---

## Data Sources

The project uses the Brazilian E-Commerce Public Dataset by Olist.

The raw dataset contains information about:

- Customers
- Orders
- Order items
- Payments
- Reviews
- Products
- Sellers
- Product categories
- Geolocation
- Category translations

---

## Pipeline Processing

### 1. Data Extraction

Raw CSV files are read using Python and Pandas.

For CI and automated testing, lightweight test fixtures are used instead of depending on the full raw dataset.

### 2. Data Transformation

The ETL pipeline combines the required datasets and creates an analytics-ready order-item fact dataset.

Key transformations include:

- Joining orders with order items
- Joining customer information
- Joining product information
- Translating product categories
- Calculating item-level revenue
- Calculating delivery duration
- Identifying late deliveries
- Handling missing values
- Validating important fields

The resulting processed dataset is stored as:

```text
data/processed/order_items_fact.parquet
```

### 3. Data Quality

The pipeline performs validation checks including:

- Duplicate order-item detection
- Critical null checks
- Monetary value validation
- Delivery-day validation
- Dataset structure validation

Automated tests are implemented using `pytest`.

---

## PostgreSQL Data Warehouse

The processed data is loaded into PostgreSQL as part of the warehouse layer.

The warehouse provides a structured environment for analytical SQL queries and separates the transformation layer from downstream analytics.

The warehouse loading process is implemented in the project and integrated with the orchestration workflow.

---

## Apache Airflow Orchestration

Apache Airflow is used to orchestrate the data pipeline.

The Airflow workflow coordinates:

```text
ETL Pipeline
     |
     v
Data Transformation
     |
     v
Data Quality Validation
     |
     v
PostgreSQL Warehouse Loading
```

This allows the pipeline to be executed as a scheduled and repeatable workflow rather than relying on manually running individual Python scripts.

---

## Automated Testing & CI

The project uses `pytest` for automated testing.

GitHub Actions automatically executes the test suite when changes are pushed to the repository or submitted through a pull request.

The CI workflow:

1. Checks out the repository
2. Sets up Python
3. Installs project dependencies
4. Runs the automated test suite

The pipeline uses test fixtures so CI does not depend on the large raw Olist dataset being present in GitHub.

---

## Project Structure

```text
ecommerce-data-engineering/
│
├── config/
│
├── dags/
│   └── ...
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── warehouse/
│
├── docker/
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── src/
│   └── etl/
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       ├── data_quality.py
│       └── pipeline.py
│
├── tests/
│   └── fixtures/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Project Progress

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Environment & Project Setup | ✅ Complete |
| Phase 2 | Data Exploration | ✅ Complete |
| Phase 3 | End-to-End ETL Pipeline | ✅ Complete |
| Phase 4 | GitHub Actions CI & Automated Testing | ✅ Complete |
| Phase 5 | PostgreSQL Data Warehouse Loader | ✅ Complete |
| Phase 6 | Apache Airflow Orchestration | ✅ Complete |
| Phase 7 | Upcoming | 🔄 Not Started |

---

## Key Project Results

The pipeline processes the Olist e-commerce dataset and produces an analytics-ready order-item fact dataset.

The processed fact table contains approximately **112,650 order-item records** and combines information from multiple source datasets.

The project also includes automated tests and a GitHub Actions CI pipeline to validate changes before they are merged or deployed.

---

## Running the Project

Create and activate the Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
python -m pytest -v
```

The ETL pipeline and warehouse loading process can also be executed through the project's Apache Airflow workflow.

---

## Git Workflow

The project uses Git for version control and GitHub for repository hosting.

Major development phases are committed separately to maintain a clear project history.

Example:

```bash
git status
git add .
git commit -m "Description of changes"
git push origin master
```

---

## Future Enhancements

Potential future improvements include:

- Cloud object storage integration
- Additional analytical models
- Advanced data quality monitoring
- Production deployment
- Pipeline monitoring and alerting
- Dashboard integration
- Additional warehouse dimensions and fact tables

---

## Dataset

Brazilian E-Commerce Public Dataset by Olist.

This project is intended as a learning and portfolio project demonstrating practical data engineering concepts and an end-to-end pipeline architecture.