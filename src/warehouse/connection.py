import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce_warehouse")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ecommerce_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


if not POSTGRES_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD is not set in the environment.")


DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)