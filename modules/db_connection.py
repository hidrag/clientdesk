import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Create and return a PostgreSQL database connection."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is missing from the .env file.")

    try:
        connection = psycopg.connect(
            database_url,
            autocommit=True,
            connect_timeout=10
        )
        return connection

    except psycopg.Error as error:
        raise ConnectionError(
            f"Database connection failed: {error}"
        ) from error
