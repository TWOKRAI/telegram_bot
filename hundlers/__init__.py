from aiogram import Dispatcher
from .weather_handler import register_weather_handlers
from .valute_handler import register_valute_handlers
from .reminder_handler import register_reminder_handlers
from .message_handler import register_message_handlers

def register_handlers(dp: Dispatcher):
    register_weather_handlers(dp)
    register_valute_handlers(dp)
    register_reminder_handlers(dp)
    register_message_handlers(dp)