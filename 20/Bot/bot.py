import asyncio
import logging
import os

import handlers
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)

dp = Dispatcher()
dp.include_routers(handlers.router,)


async def main():
    proxy_url = "http://45.88.0.117:3128"
    session = AiohttpSession(proxy=proxy_url)

    load_dotenv()
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN'), session=session)
    try:
        logging.info("Запуск бота...")
        await dp.start_polling(bot)
    finally:
        logging.info("Остановка бота...")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
