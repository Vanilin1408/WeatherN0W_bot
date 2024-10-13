import aiohttp
import asyncio
import datetime
import config


class WeatherAPI:
    """
    Класс для запросов данных через API сервиса OpenWeatherMap.

    Attributes:
        __API_KEY: str, ключ API для доступа к данным
    """

    def __init__(self, api_key: str) -> None:
        """
        Инициализация ключа API

        Args:
            api_key (str): Ключ API сервиса погоды OpenWeatherMap
        """
        self.__API_KEY: str = api_key

    async def get_weather_info_by_city(self, city_name: str) -> str:
        """
        Метод для изъятия характеристик погоды по названию города

        Args:
            city_name (string): Название города.
        Returns:
            str: Отформатированная строка с данными о погоде с параметрами:
                    "city_name" - название города,
                    "temperature" - температура град. С,
                    "humidity" - влажность %,
                    "wind_speed" - скорость ветра м/с,
                    "pressure" - давление гПа,
                    "cloudiness" - процент облачности,
                    "description" - краткое описание,
                    "sunrise" - время рассвета,
                    "sunset" - время заката.
        """

        # Базовый путь для получения данных по названию города
        url_for_current_city: str = (f"https://api.openweathermap.org/data/2.5/weather?"
                                     f"q={city_name}&appid={self.__API_KEY}&units=metric&lang=ru")

        timeout = aiohttp.ClientTimeout(total=4)  # Устанавливаем таймер максимального ожидания ответа API

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url_for_current_city) as response:
                    if response.status == 404:
                        return (f"Ошибка запроса данных с сервера. "
                                f"Убедитесь в том, что город {city_name} существует, а также в правильности написания "
                                f"названия города.")
                    elif response.status != 200:
                        return f"Ошибка запроса данных с сервера: код {response.status}"

                    raw_data: dict = await response.json()

                    weather_data: dict = {
                        "city_name": raw_data["name"],
                        "temperature": raw_data["main"]["temp"],
                        "humidity": raw_data["main"]["humidity"],
                        "wind_speed": raw_data["wind"]["speed"],
                        "pressure": raw_data["main"]["pressure"],
                        "cloudiness": raw_data["clouds"]["all"],
                        "description": raw_data["weather"][0]["description"],
                        "sunrise": datetime.datetime.fromtimestamp(raw_data["sys"]["sunrise"]).strftime("%Y-%m-%d "
                                                                                                        "%H:%M:%S"),
                        "sunset": datetime.datetime.fromtimestamp(raw_data["sys"]["sunset"]).strftime("%Y-%m-%d "
                                                                                                      "%H:%M:%S")
                    }

                    str_weather_report: str = (
                        f"<b>Город</b>: {weather_data['city_name']},\n"
                        f"<b>Температура</b>: {weather_data['temperature']} °C,\n"
                        f"<b>Влажность</b>: {weather_data['humidity']} %,\n"
                        f"<b>Скорость ветра</b>: {weather_data['wind_speed']} м/с,\n"
                        f"<b>Давление</b>: {weather_data['pressure']} гПа,\n"
                        f"<b>Облачность</b>: {weather_data['cloudiness']} %,\n"
                        f"<b>Описание</b>: {weather_data['description'].capitalize()},\n"
                        f"Время <b>рассвета</b>: {weather_data['sunrise']},\n"
                        f"Время <b>заката</b>: {weather_data['sunset']}."
                    )

                    return str_weather_report

        except asyncio.TimeoutError:
            return "Ошибка запроса данных с сервера: превышено время ожидания ответа."
        except aiohttp.ClientConnectorError:
            return "Ошибка запроса данных с сервера: не удалось подключится к серверу"
        except Exception as e:
            return f"Ошибка: {str(e)}"


# Тестирование
if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        weather = WeatherAPI(config.API_KEY)
        test_data: str = await weather.get_weather_info_by_city("london")
        print(test_data)

        return

    asyncio.run(main())
