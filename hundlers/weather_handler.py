import aiohttp
import logging

from morph_module import convert_to_nominative

from TOKEN import WEATHER_API_KEY


async def get_weather_data(city: str) -> str:
    city_nominative = convert_to_nominative(city)

    async with aiohttp.ClientSession() as session:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_nominative}&appid={WEATHER_API_KEY}&units=metric'
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data['cod'] == 200:
                    weather = data['weather'][0]['description']
                    temperature = data['main']['temp']
                    humidity = data['main']['humidity']
                    return f"Погода в {city}:  температура: {temperature}°C, влажность: {humidity}%"
                else:
                    return f"Не удалось получить данные о погоде для города {city}. Попробуйте другой город."
        except aiohttp.ClientError as e:
            logging.error(f"Ошибка при выполнении запроса к API погоды: {e}")
            return "Произошла ошибка при получении данных о погоде. Пожалуйста, попробуйте позже."
