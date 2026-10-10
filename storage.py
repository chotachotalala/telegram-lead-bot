"""SQLite storage for confirmed Telegram bot leads."""

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


# Keep the database next to the project's Python files, regardless of CWD.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "leads.db"

CREATE_LEADS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    name TEXT NOT NULL,
    contact TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    telegram_username TEXT DEFAULT NULL,
    created_at TEXT NOT NULL
)
"""

INSERT_LEAD_SQL = """
INSERT INTO leads (
    service,
    name,
    contact,
    user_id,
    telegram_username,
    created_at
)
VALUES (?, ?, ?, ?, ?, ?)
"""


def init_db() -> None:
    """Create the leads table if it does not exist yet.

    SQLite errors are exposed as RuntimeError so the existing confirmation
    handler can catch the failure and show its save-error message.
    """
    try:
        with closing(sqlite3.connect(DB_PATH)) as connection:
            with connection:
                connection.execute(CREATE_LEADS_TABLE_SQL)
    except sqlite3.Error as exc:
        raise RuntimeError(
            "Не удалось инициализировать базу данных SQLite."
        ) from exc


def save_lead(lead: dict[str, Any]) -> None:
    """Save one confirmed lead, preserving the existing function interface."""
    required_fields = (
        "service",
        "name",
        "contact",
        "user_id",
        "created_at",
    )
    missing_fields = [field for field in required_fields if field not in lead]
    if missing_fields:
        raise ValueError(
            "В заявке отсутствуют обязательные поля: "
            + ", ".join(missing_fields)
        )

    # Ensure the schema exists before attempting the first insert.
    init_db()

    values = (
        lead["service"],
        lead["name"],
        lead["contact"],
        lead["user_id"],
        lead.get("telegram_username"),
        lead["created_at"],
    )

    try:
        with closing(sqlite3.connect(DB_PATH)) as connection:
            with connection:
                connection.execute(INSERT_LEAD_SQL, values)
    except sqlite3.Error as exc:
        # Do not swallow the error. RuntimeError is caught by the current
        # handlers/lead.py confirmation handler, with the SQLite error chained.
        raise RuntimeError(
            "Не удалось сохранить заявку в базе данных SQLite."
        ) from exc


def get_leads() -> list[dict[str, str]]:
    """Получить сохранённые заявки из базы данных SQLite."""

    # Если базы ещё нет, заявок пока нет.
    if not DB_PATH.exists():
        return []

    try:
        with closing(sqlite3.connect(DB_PATH)) as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT service, name, contact, created_at
                FROM leads
                ORDER BY id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    except sqlite3.Error as exc:
        raise RuntimeError(
            "Не удалось прочитать заявки из базы данных SQLite."
        ) from exc
