import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import get_bot_token
from handlers.lead import router


async def main() -> None:
    """Создаёт приложение бота, подключает обработчики и запускает polling."""
    bot = Bot(token=get_bot_token())
    dp = Dispatcher()

    # Dispatcher — главный объект обработки событий.
    # В него подключаем Router с логикой нашего Lead Bot.
    dp.include_router(router)

    # Получаем информацию о боте, чтобы убедиться, что токен рабочий.
    me = await bot.get_me()

    print(f"Бот запущен: @{me.username}")

    # Запускаем получение новых сообщений от Telegram.
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Включаем базовое логирование aiogram.
    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())