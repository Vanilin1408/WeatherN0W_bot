import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from modules.WeatherAPI import WeatherAPI

# Логирование для удобства отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherTGBot:
    """
    Класс для реализации логики TG-бота

    Attributes:
        __TOKEN (str): Токен для аутентификации TG-бота.
        __API_KEY (str): Ключ API для доступа к API OpenWeatherMap.
        __app (telegram.ext.Application): Главное приложение Telegram-бота, управляющее обработчиками.
        __api_model (WeatherAPI): Объект класса для работы с API погоды.
    """

    def __init__(self, token: str, api_key: str):
        """
        Инициализация бота, модели API погоды и обработчиков

        Args:
            token (string): Токен TG-бота
            api_key (string): Ключ API сервиса погоды
        """

        logger.info("Инициализация бота...")

        self.__TOKEN = token  # Сохраняем токен бота
        self.__API_KEY = api_key  # и ключ апи
        self.__api_model = WeatherAPI(self.__API_KEY)  # Инициализация модели API погоды

        self.__app = ApplicationBuilder().token(self.__TOKEN).build()  # Инициализация приложение
        self.__setup_handlers()  # Установка обработчиков

        logger.info("Инициализация прошла успешно.")

    def __setup_handlers(self):
        """
        Метод установки обработчиков
        """
        self.__app.add_handler(CommandHandler("start", self.__start))
        self.__app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.__looped_answer))
        self.__app.add_handler(MessageHandler(~filters.TEXT, self.__non_text_message_processing))

    async def __start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработка начальной команды /start
        """
        logger.info("Выполнение команды '/start'")

        await update.message.reply_text("Здравствуйте, я бот для получения текущих данных о погоде."
                                        "\nДля предоставления информации введите название города на русском "
                                        "или английском языке")
        return

    async def __non_text_message_processing(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработка нетекстовых сообщений: удаление и указание на ввод только текстовых сообщений
        """

        logger.info("Выполнение обработки для нетекстовых сообщений")

        # Удаление нетекстовых сообщений пользователя
        await update.message.delete()
        await update.message.reply_text("Бот поддерживает только текстовые запросы с названием требуемого города "
                                        "на русском или английском языке.")

        return

    async def __looped_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Зацикленный обработчик для вывода прогноза погоды по введенному городу
        """
        logger.info(f"Выполнение запроса погодной информации по введенному названию '{str(update.message.text)}'")

        weather_info: str = await self.__api_model.get_weather_info_by_city(str(update.message.text).lower())

        await update.message.reply_text((weather_info + "\n\n Для дальнейшей работы введите город: "), parse_mode="HTML")
        return

    def run(self):
        """
        Метод запуска бота ("опроса")
        """
        self.__app.run_polling()


# Тестирование
if __name__ == "__main__":
    import config

    bot = WeatherTGBot(config.BOT_TOKEN, config.API_KEY)
    bot.run()
