from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def services_keyboard(services: list[str]) -> InlineKeyboardMarkup:
    """Создаёт inline-клавиатуру со списком услуг."""

    buttons = [
        [
            InlineKeyboardButton(
                text=service,

                # Это значение Telegram вернёт нам
                # после нажатия пользователем кнопки.
                callback_data=f"service:{service}",
            )
        ]
        for service in services
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )