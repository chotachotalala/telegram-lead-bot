import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import get_bot_token, load_config
from handlers.lead import router


async def main() -> None:
    # Проверяем конфигурацию перед запуском бота.
    # Validate the configuration before starting the bot.
    load_config()

    bot = Bot(token=get_bot_token())
    dp = Dispatcher()

    # Подключаем обработчики заявок.
    # Register the lead handlers.
    dp.include_router(router)

    try:
        # Проверяем подключение к Telegram.
        # Verify the connection to Telegram.
        me = await bot.get_me()
        print(f"Бот запущен: @{me.username}")
        print("Для остановки нажмите Ctrl + C.")

        # Запускаем обработку сообщений.
        # Start processing Telegram updates.
        await dp.start_polling(bot)

    finally:
        # Закрываем соединение при завершении работы.
        # Close the connection when the bot shuts down.
        await bot.session.close()


if __name__ == "__main__":
    # Настраиваем журналирование событий бота.
    # Configure logging for bot events.
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Показываем спокойное сообщение вместо трассировки ошибки.
        # Print a clean message instead of a traceback.
        print("\nБот остановлен." )