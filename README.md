# Telegram Lead Bot

Учебный проект Telegram-бота.

## День 2

На этом этапе реализована работа с JSON-конфигурацией.

Файлы:

- `bot_config.json` — настройки бота
- `config.py` — загрузка и сохранение настроек
- `bot.py` — использование настроек проекта

## Запуск

```bash
python config.py
python bot.py

# Telegram Lead Bot

Учебный Telegram-бот на Python и aiogram.

## День 3

Реализовано:

- подключение Telegram Bot Token через `.env`
- создание `Bot`
- создание `Dispatcher`
- обработчик `/start`
- запуск polling
- загрузка `welcome_message` из `bot_config.json`

## Запуск

Активировать виртуальное окружение и выполнить:

```bash
python bot.py