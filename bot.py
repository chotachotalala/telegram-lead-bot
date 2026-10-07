import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from config import load_config


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

config = load_config()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(config["welcome_message"])


async def main():
    me = await bot.get_me()

    print(f"Бот запущен: @{me.username}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())