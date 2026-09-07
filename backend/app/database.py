import os
from contextlib import contextmanager

import psycopg2


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5432/land_records"
)


@contextmanager
def get_connection():
    connection = psycopg2.connect(DATABASE_URL)
    try:
        yield connection
    finally:
        connection.close()

