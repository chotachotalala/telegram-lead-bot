import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

required = (
    "PGHOST",
    "PGDATABASE",
    "PGUSER",
    "PGPASSWORD",
)

missing = [key for key in required if not os.getenv(key)]

if missing:
    raise RuntimeError(
        "Не заданы параметры подключения: "
        + ", ".join(missing)
    )

with psycopg.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT", "5432"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user, version()"
        )
        print(cursor.fetchone())