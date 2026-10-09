import json
import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


# Храним заявки рядом с основным файлом бота.
# Store leads next to the main bot file.
BASE_DIR = Path(__file__).resolve().parent
LEADS_FILE = BASE_DIR / "leads.json"
TEMP_FILE = BASE_DIR / "leads.json.tmp"


def save_lead(lead: dict[str, Any]) -> None:
    # Загружаем существующие заявки или начинаем с пустого списка.
    # Load existing leads or start with an empty list.
    if LEADS_FILE.exists():
        try:
            with LEADS_FILE.open("r", encoding="utf-8") as file:
                leads = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Файл leads.json содержит некорректный JSON."
            ) from exc

        if not isinstance(leads, list):
            raise ValueError(
                "Файл leads.json должен содержать список заявок."
            )

        if any(not isinstance(item, dict) for item in leads):
            raise ValueError(
                "Файл leads.json содержит заявки неправильного формата."
            )
    else:
        leads = []

    leads.append(lead)

    # Сначала записываем временный файл, затем заменяем основной.
    # Write a temporary file first, then replace the main file.
    try:
        with TEMP_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                leads,
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.write("\n")

        TEMP_FILE.replace(LEADS_FILE)

    except Exception:
        # Удаляем временный файл при неудачном сохранении.
        # Remove the temporary file if saving fails.
        try:
            TEMP_FILE.unlink(missing_ok=True)
        except OSError:
            logger.exception(
                "Не удалось удалить временный файл leads.json.tmp."
            )

        raise