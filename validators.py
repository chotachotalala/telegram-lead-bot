import re


# Подготавливаем регулярные выражения для проверки контактных данных.
# Define regular expressions for validating contact information.
PHONE_PATTERN = re.compile(r"^\+?[\d\s().-]+$")

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)

TELEGRAM_USERNAME_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]{4,31}$"
)


def is_valid_phone(value: str) -> bool:
    value = value.strip()

    if not PHONE_PATTERN.fullmatch(value):
        return False

    digits_count = sum(
        character.isdigit()
        for character in value
    )

    return 7 <= digits_count <= 15


def is_valid_email(value: str) -> bool:
    value = value.strip()
    return bool(EMAIL_PATTERN.fullmatch(value))


def is_valid_telegram_username(value: str) -> bool:
    username = value.strip()

    # Разрешаем ввод имени пользователя как с @, так и без него.
    # Allow usernames to be entered with or without @.
    if username.startswith("@"):
        username = username[1:]

    return bool(
        TELEGRAM_USERNAME_PATTERN.fullmatch(username)
    )