import asyncio

from my_bot import TelegramBot

from TOKEN import API_TOKEN


if __name__ == '__main__':
    bot_instance = TelegramBot(API_TOKEN)
    asyncio.run(bot_instance.start_polling())
