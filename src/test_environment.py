import pandas as pd
import numpy as np
import sqlalchemy
import psycopg2
import requests
import dotenv
import openpyxl
import pyarrow


def main():
    print("E-Commerce Data Engineering Environment")
    print("-" * 45)
    print(f"Pandas: {pd.__version__}")
    print(f"NumPy: {np.__version__}")
    print(f"SQLAlchemy: {sqlalchemy.__version__}")
    print("PostgreSQL driver: psycopg2")
    print("Requests: installed")
    print("python-dotenv: installed")
    print("OpenPyXL: installed")
    print("PyArrow: installed")
    print("-" * 45)
    print("Environment setup successful!")


if __name__ == "__main__":
    main()