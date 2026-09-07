import os
import random

import psycopg2
from faker import Faker
from psycopg2.extras import execute_values
from shapely.geometry import box

RECORD_COUNT = 500
HALIYAL_LAT, HALIYAL_LON = 15.3344, 74.7671
BOUNDING_BOX_OFFSET = 0.18
HISSA_NUMBERS = ["*", "1", "2A", "2B", "3", "4A"]
LAND_TYPES = ["Agricultural", "Commercial", "Residential", "Government"]
LAND_TYPE_WEIGHTS = [70, 15, 10, 5]
TAX_STATUSES = ["Paid", "Pending", "Overdue"]
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/land_records")


def unique_survey_hissa_pairs(count: int):
    pairs = [(str(number), hissa) for number in range(1, 801) for hissa in HISSA_NUMBERS]
    return random.sample(pairs, count)


def parcel_wkt() -> str:
    latitude = random.uniform(HALIYAL_LAT - BOUNDING_BOX_OFFSET, HALIYAL_LAT + BOUNDING_BOX_OFFSET)
    longitude = random.uniform(HALIYAL_LON - BOUNDING_BOX_OFFSET, HALIYAL_LON + BOUNDING_BOX_OFFSET)
    width = random.uniform(0.0005, 0.001)
    height = random.uniform(0.0005, 0.001)
    return box(longitude - width / 2, latitude - height / 2, longitude + width / 2, latitude + height / 2).wkt


def generate_records():
    fake = Faker("en_IN")
    return [
        (
            survey, hissa, fake.name(),
            random.choices(LAND_TYPES, weights=LAND_TYPE_WEIGHTS, k=1)[0],
            random.choice(TAX_STATUSES), "Haliyal", parcel_wkt(),
        )
        for survey, hissa in unique_survey_hissa_pairs(RECORD_COUNT)
    ]


def main():
    query = """
        INSERT INTO official_land_records
        (survey_number, hissa_number, owner_name, land_type, tax_status, village_name, geom)
        VALUES %s
        ON CONFLICT (survey_number, hissa_number) DO NOTHING
    """
    try:
        with psycopg2.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
            execute_values(cursor, query, generate_records(),
                           template="(%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))")
            print(f"Inserted {cursor.rowcount} synthetic land records.")
    except psycopg2.Error as error:
        print(f"Database error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

