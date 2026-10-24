"""Хранение подтверждённых заявок в PostgreSQL."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def connect_db() -> psycopg.Connection:
    """Открыть подключение к PostgreSQL."""
    required = (
        "PGHOST",
        "PGDATABASE",
        "PGUSER",
        "PGPASSWORD",
    )

    missing = [
        key
        for key in required
        if not os.getenv(key)
    ]

    if missing:
        raise RuntimeError(
            "Не заданы параметры подключения: "
            + ", ".join(missing)
        )

    return psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        row_factory=dict_row,
    )


def save_lead(lead: dict[str, Any]) -> None:
    """Сохранить пользователя и его заявку в одной транзакции."""
    required_fields = (
        "service",
        "name",
        "contact",
        "user_id",
        "created_at",
    )

    missing = [
        field
        for field in required_fields
        if field not in lead
    ]

    if missing:
        raise ValueError(
            "В заявке отсутствуют обязательные поля: "
            + ", ".join(missing)
        )

    created_at = lead["created_at"]

    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)

    if not isinstance(created_at, datetime):
        raise ValueError(
            "created_at должен быть датой или ISO-строкой."
        )

    try:
        with connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (
                        telegram_id,
                        telegram_username
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (telegram_id)
                    DO UPDATE SET
                        telegram_username =
                            EXCLUDED.telegram_username
                    """,
                    (
                        lead["user_id"],
                        lead.get("telegram_username"),
                    ),
                )

                cursor.execute(
                    """
                    INSERT INTO leads (
                        service,
                        name,
                        contact,
                        user_id,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        lead["service"],
                        lead["name"],
                        lead["contact"],
                        lead["user_id"],
                        created_at,
                    ),
                )

    except psycopg.Error as exc:
        raise RuntimeError(
            "Не удалось сохранить заявку в PostgreSQL."
        ) from exc


def get_leads() -> list[dict[str, Any]]:
    """Получить заявки от новых к старым."""
    try:
        with connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        service,
                        name,
                        contact,
                        created_at
                    FROM leads
                    ORDER BY created_at DESC, id DESC
                    """
                )
                return cursor.fetchall()

    except psycopg.Error as exc:
        raise RuntimeError(
            "Не удалось прочитать заявки из PostgreSQL."
        ) from exc