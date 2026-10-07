import json


def load_config():
    with open("bot_config.json", "r", encoding="utf-8") as file:
        return json.load(file)