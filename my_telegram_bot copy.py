import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import aiohttp
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, NewsNERTagger, Doc
from textblob import TextBlob

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
from TOKEN import API_TOKEN, WEATHER_API_KEY, VALUTE_API_KEY

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

WHILE_DOLLAR = False

# Инициализация морфологического анализатора
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)

def convert_to_nominative(city: str) -> str:
    """
    Функция для преобразования названия города в именительный падеж.
    """
    doc = Doc(city)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
        if token.lemma:
            return token.lemma
    return city

def contains_any_word(word_list, string):
    # Преобразуем строку и слова к нижнему регистру
    string = string.lower()
    word_list = [word.lower() for word in word_list]

    # Проверяем каждое слово из списка
    for word in word_list:
        if word in string:
            return True
    return False

def find_next_word(target_word, string):
    print('find_next_word', string, target_word)
    # Преобразуем строку и целевое слово к нижнему регистру
    string_lower = string.lower()
    target_word_lower = target_word.lower()

    target_word_nominative = convert_to_nominative(target_word_lower)

    # Разбиваем строку на слова
    words = string.split()
    words_lower = string_lower.split()

    # Ищем индекс целевого слова
    try:
        index = words_lower.index(target_word_nominative)
    except ValueError:
        return None  # Целевое слово не найдено

    # Проверяем, есть ли следующее слово
    if index + 1 < len(words):
        return words[index + 1]
    else:
        return None  # Нет следующего слова


def analyze_sentiment(text: str) -> str:
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'позитивное'
    elif analysis.sentiment.polarity == 0:
        return 'нейтральное'
    else:
        return 'негативное'

# Создаем клавиатуру с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/start')],
        [KeyboardButton(text='/weather'), KeyboardButton(text='/valute')],
        [KeyboardButton(text='/delete')],
        [KeyboardButton(text='/dollar'), KeyboardButton(text='/nodollar')]
    ],
    resize_keyboard=True
)


import datetime

# Глобальный словарь для хранения напоминаний
reminders = {}

async def set_reminder(message: Message, time: int, reminder_text: str):
    """
    Функция для установки напоминания.

    :param message: Сообщение от пользователя.
    :param time: Время в секундах, через которое нужно отправить напоминание.
    :param reminder_text: Текст напоминания.
    """
    chat_id = message.chat.id
    reminder_time = datetime.datetime.now() + datetime.timedelta(seconds=time)
    reminders[chat_id] = (reminder_time, reminder_text)
    await bot.send_message(chat_id, f"Напоминание установлено на {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")

async def send_reminder():
    """
    Функция для отправки напоминания.
    """
    while True:
        now = datetime.datetime.now()
        to_remove = []
        for chat_id, (reminder_time, reminder_text) in reminders.items():
            if now >= reminder_time:
                await bot.send_message(chat_id, reminder_text)
                to_remove.append(chat_id)

        for chat_id in to_remove:
            del reminders[chat_id]

        await asyncio.sleep(1)  # Проверяем напоминания каждую секунду

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

# Запуск функции отправки напоминаний в фоновом режиме
async def main():
    asyncio.create_task(send_reminder())
    await dp.start_polling(bot)

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

@dp.message(Command(commands=['dollar']))
async def dollar_start(message: Message):
    print(f"Выполняется функция: hi1")
    global WHILE_DOLLAR
    WHILE_DOLLAR = True

    while WHILE_DOLLAR:
        await get_valute(message)
        await asyncio.sleep(3600)

@dp.message(Command(commands=['nodollar']))
async def dollar_stop(message: Message):
    print(f"Выполняется функция: hi2")
    global WHILE_DOLLAR
    WHILE_DOLLAR = False
    await message.reply(f"Закончил", reply_markup=keyboard)

def write_in_file(file: str, message: str):
    with open('messages.txt', 'a', encoding='utf-8') as file:
        file.write(message)

def read_all_file(file_path: str) -> str:
    """
    Функция для чтения всего текста из файла и возврата его в виде строки.

    :param file_path: Путь к файлу.
    :return: Содержимое файла в виде строки.
    """

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"Файл {file_path} не найден."
    except Exception as e:
        return f"Произошла ошибка при чтении файла: {e}"

@dp.message()
async def save_message(message: Message):
    bot_message = ''
    user_message = message.text

    sentiment = analyze_sentiment(user_message)
    

    write_in_file('messages.txt', f"Я: {message.text}\n")

    if contains_any_word(["удалить", "очистить", "удали"], user_message):
        await delete_message_data()
        await message.reply('История очищена', reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: {bot_message}\n")
        return

    if contains_any_word(["погода", "погодка", "температура", "погоды", "градусов"], user_message):
        city = find_next_word('в', str(user_message))
        bot_message = await get_weather_data(city)
        await message.reply(bot_message, reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: {bot_message}\n")
        return

    if contains_any_word(["валют", "валюты", "курс"], user_message):
        bot_message = await get_valute_data()
        await message.reply(bot_message, reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: {bot_message}\n")
        return

    if contains_any_word(["история", "историю"], user_message):
        bot_message = read_all_file('messages.txt')
        await message.reply(f"История сообщений:\n {bot_message}\n", reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: История сообщений:\n {bot_message}\n")
        return

    if contains_any_word(["история", "историю", "переписку"], user_message):
        bot_message = read_all_file('messages.txt')
        await message.reply(f"История сообщений:\n {bot_message}\n", reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: История сообщений:\n {bot_message}\n")
        return

    if contains_any_word(["здарова", "привет", "здорова"], user_message):
        await bot.send_message(message.chat.id, f"Здравствуйте, {message.chat.first_name}! \n")

        write_in_file('messages.txt', f"Здравствуйте\n")
        return

    if contains_any_word(["настроение"], user_message):
        await bot.send_message(message.chat.id, f"Ваше настроение я оцениваю {sentiment}.")

        write_in_file('messages.txt', f"Здравствуйте\n")
        return


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
