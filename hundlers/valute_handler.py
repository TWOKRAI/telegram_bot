import aiohttp
import logging

from config import VALUTE_API_KEY

async def get_valute_data():
    async with aiohttp.ClientSession() as session:
        url = f'https://openexchangerates.org/api/latest.json?app_id={VALUTE_API_KEY}'
        try:
            async with session.get(url) as response:
                data = await response.json()
                return f"Курс доллара к рублю {data['rates']['RUB']}"
        except aiohttp.ClientError as e:
            logging.error(f"Ошибка при выполнении запроса к API погоды: {e}")
            return "Произошла ошибка при получении данных о погоде. Пожалуйста, попробуйте позже."
