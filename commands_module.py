import asyncio
import aiohttp
from aiogram.filters import Command

from my_bot import bot, dp, Message, keyboard, logging
from morph_module import convert_to_nominative
from reminder_module import set_reminder

from TOKEN import WEATHER_API_KEY, VALUTE_API_KEY

# Функция для обработки команды /reminder
@dp.message(Command(commands=['reminder']))
async def reminder(message: Message):
    try:
        _, time_str, *reminder_text = message.text.split(' ', 2)
        time = int(time_str)
        reminder_text = ' '.join(reminder_text)
        await set_reminder(message, time, reminder_text)
    except ValueError:
        await bot.send_message(message.chat.id, "Используйте команду в формате: /reminder <время в секундах> <текст напоминания>")

# Функция для обработки команды /start
@dp.message(Command(commands=['start']))
async def send_welcome(message: Message):
    await message.reply("Привет! Отправь мне сообщение, и я сохраню его в текстовый файл.", reply_markup=keyboard)

async def delete_message_data():
    with open('messages.txt', 'w', encoding='utf-8') as file:
        pass

# Функция для обработки команды /delete
@dp.message(Command(commands=['delete']))
async def delete_message(message: Message):
    await delete_message_data()
    await message.reply("История очищена!", reply_markup=keyboard)

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

@dp.message(Command(commands=['weather']))
async def get_weather(message: Message):
    print('weather', message.text)
    city = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else None
    if not city:
        await message.reply("Пожалуйста, укажите город. Например: /weather Москва", reply_markup=keyboard)
        return

    bot_message = await get_weather_data(city)
    await message.reply(bot_message, reply_markup=keyboard)

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

# Функция для обработки команды /weather
@dp.message(Command(commands=['valute']))
async def get_valute(message: Message):
    bot_message = await get_valute_data()
    await message.reply(bot_message, reply_markup=keyboard)
