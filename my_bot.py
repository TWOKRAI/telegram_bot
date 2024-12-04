import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import aiohttp
from aiogram.filters import Command

from text_file import write_in_file, read_all_file, delete_message_data
from morph_module import contains_any_word, find_next_word, analyze_sentiment
from reminder_module import set_reminder
from weather_module import get_weather_data
from valute_module import get_valute_data


# Включаем логирование
logging.basicConfig(level=logging.INFO)


class TelegramBot:
    def __init__(self, api_token):
        self.bot = Bot(token=api_token)
        self.dp = Dispatcher()
        self.keyboard = self._create_keyboard()
        self._register_handlers()


    def _create_keyboard(self):
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='/start')],
                [KeyboardButton(text='/weather'), KeyboardButton(text='/valute')],
                [KeyboardButton(text='/delete')],
                [KeyboardButton(text='/dollar'), KeyboardButton(text='/nodollar')]
            ],
            resize_keyboard=True
        )


    async def start_polling(self):
        await self.dp.start_polling(self.bot)
    

    def _register_handlers(self):
        self.dp.message.register(self.start, Command(commands=['start']))
        self.dp.message.register(self.reminder, Command(commands=['reminder']))
        self.dp.message.register(self.delete_message, Command(commands=['delete']))
        self.dp.message.register(self.get_weather, Command(commands=['weather']))
        self.dp.message.register(self.get_valute, Command(commands=['valute']))
        self.dp.message.register(self.chat)


    async def start(self, message: Message):
        await message.reply("Привет! Отправь мне сообщение, и я сохраню его в текстовый файл.", reply_markup=self.keyboard)


    async def reminder(self, message: Message):
        try:
            _, time_str, *reminder_text = message.text.split(' ', 2)
            time = int(time_str)
            reminder_text = ' '.join(reminder_text)
            await set_reminder(message, time, reminder_text)
        except ValueError:
            await self.bot.send_message(message.chat.id, "Используйте команду в формате: /reminder <время в секундах> <текст напоминания>")


    async def delete_message(self, message: Message):
        await delete_message_data()
        await message.reply("История очищена!", reply_markup=self.keyboard)


    async def get_weather(self, message: Message):
        print('weather', message.text)
        city = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else None
        if not city:
            await message.reply("Пожалуйста, укажите город. Например: /weather Москва", reply_markup=self.keyboard)
            return

        bot_message = await get_weather_data(city)
        await message.reply(bot_message, reply_markup=self.keyboard)


    async def get_valute(self, message: Message):
        bot_message = await self.get_valute_data()
        await message.reply(bot_message, reply_markup=self.keyboard)


    async def chat(self,message: Message):
        bot_message = ''
        user_message = message.text

        sentiment = analyze_sentiment(user_message)
        

        write_in_file('messages.txt', f"Я: {message.text}\n")

        if contains_any_word(["удалить", "очистить", "удали"], user_message):
            await delete_message_data()
            await message.reply('История очищена', reply_markup=self.keyboard)

            write_in_file('messages.txt', f"Бот: {bot_message}\n")
            return

        if contains_any_word(["погода", "погодка", "температура", "погоды", "градусов"], user_message):
            city = find_next_word('в', str(user_message))
            bot_message = await get_weather_data(city)
            await message.reply(bot_message)

            write_in_file('messages.txt', f"Бот: {bot_message}\n")
            return

        if contains_any_word(["валют", "валюты", "курс"], user_message):
            bot_message = await get_valute_data()
            await message.reply(bot_message)

            write_in_file('messages.txt', f"Бот: {bot_message}\n")
            return

        if contains_any_word(["история", "историю"], user_message):
            bot_message = read_all_file('messages.txt')
            await message.reply(f"История сообщений:\n {bot_message}\n")

            write_in_file('messages.txt', f"Бот: История сообщений:\n {bot_message}\n")
            return

        if contains_any_word(["история", "историю", "переписку"], user_message):
            bot_message = read_all_file('messages.txt')
            await message.reply(f"История сообщений:\n {bot_message}\n")

            write_in_file('messages.txt', f"Бот: История сообщений:\n {bot_message}\n")
            return

        if contains_any_word(["здарова", "привет", "здорова"], user_message):
            await self.bot.send_message(message.chat.id, f"Здравствуйте, {message.chat.first_name}! \n")

            write_in_file('messages.txt', f"Здравствуйте\n")
            return

        if contains_any_word(["настроение"], user_message):
            await self.bot.send_message(message.chat.id, f"Ваше настроение я оцениваю {sentiment}.")

            write_in_file('messages.txt', f"Здравствуйте\n")
            return