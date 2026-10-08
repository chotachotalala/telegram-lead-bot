import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

# Загружаем переменные из .env независимо от того,
# из какой директории была запущена программа.
load_dotenv(BASE_DIR / ".env")


def get_bot_token() -> str:
    """Возвращает токен бота или сообщает об ошибке."""
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "BOT_TOKEN не найден. Создайте файл .env "
            "и добавьте туда BOT_TOKEN=ваш_токен."
        )

    return token


def load_config() -> dict[str, Any]:
    """Загружает публичную конфигурацию бота из JSON."""
    config_path = BASE_DIR / "bot_config.json"

    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)