import datetime
import asyncio
from aiogram.types import Message

# Глобальный словарь для хранения напоминаний
reminders = {}

async def set_reminder(bot, message: Message, time: int, reminder_text: str):
    """
    Функция для установки напоминания.

    :param bot: Экземпляр бота.
    :param message: Сообщение от пользователя.
    :param time: Время в секундах, через которое нужно отправить напоминание.
    :param reminder_text: Текст напоминания.
    """
    chat_id = message.chat.id
    reminder_time = datetime.datetime.now() + datetime.timedelta(seconds=time)
    reminders[chat_id] = (reminder_time, reminder_text)
    await bot.send_message(chat_id, f"Напоминание установлено на {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")

async def send_reminder(bot):
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