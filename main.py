# Импорт написанных модулей
from modules.bot import WeatherTGBot
# Конфиг
import config


def main() -> int:
    bot = WeatherTGBot(config.BOT_TOKEN, config.API_KEY)
    bot.run()

    return 0


if __name__ == "__main__":
    print(main())
