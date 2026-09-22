# The official Airflow image already includes compatible pandas and pyarrow
# versions, which are all the existing ETL needs. Do not install the project's
# full requirements here: its newer SQLAlchemy version is incompatible with
# Airflow 2.10's metadata database.
FROM apache/airflow:2.10.5-python3.12
