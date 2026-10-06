import json
from pathlib import Path


CONFIG_FILE = Path(__file__).resolve().parent / "bot_config.json"


def load_config() -> dict:
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_config(config: dict) -> None:
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            config,
            file,
            ensure_ascii=False,
            indent=4
        )


if __name__ == "__main__":
    config = load_config()

    print(config["bot_name"])
    print(config["admin_id"])
    print(config["services"])
    print(config["services"][0])

    new_service = "CRM-интеграция"

    if new_service not in config["services"]:
        config["services"].append(new_service)
        save_config(config)
        print(f"Добавлена новая услуга: {new_service}")
    else:
        print(f"Услуга уже существует: {new_service}")