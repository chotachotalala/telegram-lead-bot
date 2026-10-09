import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


# Находим файлы проекта независимо от текущей рабочей директории.
# Resolve project files independently of the current working directory.
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def get_bot_token() -> str:
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "BOT_TOKEN не найден. Создайте файл .env "
            "и добавьте туда BOT_TOKEN=ваш_токен."
        )

    return token


def load_config() -> dict[str, Any]:
    config_path = BASE_DIR / "bot_config.json"

    # Читаем конфигурацию и обрабатываем ошибки файла и JSON.
    # Read the configuration and handle file and JSON errors.
    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except OSError as exc:
        raise RuntimeError(
            f"Не удалось прочитать файл {config_path.name}."
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Файл {config_path.name} содержит некорректный JSON "
            f"(строка {exc.lineno}, столбец {exc.colno})."
        ) from exc

    if not isinstance(config, dict):
        raise ValueError(
            "Конфигурация должна содержать JSON-объект."
        )

    # Проверяем наличие обязательных параметров.
    # Validate the presence of required configuration keys.
    required_keys = ("welcome_message", "services", "admin_id")
    missing_keys = [
        key for key in required_keys
        if key not in config
    ]

    if missing_keys:
        raise ValueError(
            "В bot_config.json отсутствуют обязательные ключи: "
            + ", ".join(missing_keys)
        )

    # Проверяем тип и содержимое приветственного сообщения.
    # Validate the welcome message type and content.
    welcome_message = config["welcome_message"]

    if (
        not isinstance(welcome_message, str)
        or not welcome_message.strip()
    ):
        raise ValueError(
            "Параметр welcome_message должен быть непустой строкой."
        )

    # Проверяем список услуг перед созданием кнопок.
    # Validate the services list before creating buttons.
    services = config["services"]

    if not isinstance(services, list) or not services:
        raise ValueError(
            "Параметр services должен быть непустым списком."
        )

    if any(
        not isinstance(service, str) or not service.strip()
        for service in services
    ):
        raise ValueError(
            "Каждая услуга в services должна быть непустой строкой."
        )

    # Проверяем, что ID администратора является положительным числом.
    # Ensure the administrator ID is a positive integer.
    admin_id = config["admin_id"]

    if (
        not isinstance(admin_id, int)
        or isinstance(admin_id, bool)
        or admin_id <= 0
    ):
        raise ValueError(
            "Параметр admin_id должен быть положительным целым числом."
        )

    return config