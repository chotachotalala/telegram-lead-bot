from config import load_config


config = load_config()


print("Название бота:", config["bot_name"])

print("Услуги:")

for service in config["services"]:
    print("-", service)