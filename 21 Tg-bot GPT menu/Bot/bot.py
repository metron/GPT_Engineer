import asyncio
import logging
import os

import handlers
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    # Устанавливаем уровень INFO, чтобы записывать уровни логирования: INFO, WARNING, ERROR, CRITICAL
    level=logging.INFO,
    # Формат сообщения, включающий временную метку, имя логгера, уровень логирования и само сообщение
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'),  # Запись логов в файл "bot.log" для дальнейшего анализа
              logging.StreamHandler()])  # Вывод логов в консоль для отслеживания работы в реальном времени

load_dotenv() # Загружаем переменные окружения из файла .env

dp = Dispatcher(storage=MemoryStorage())
# Включаем маршрутизаторы (роутеры) команд и обработчиков в объект dp для обработки входящих сообщений
dp.include_routers(handlers.router,)

# -------------------------------------------------------------

async def main():
    # proxy_url = "http://43.99.54.236:5555"
    proxy_url = "http://167.103.115.102:8800"
    session = AiohttpSession(proxy=proxy_url)

    load_dotenv()
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN'), session=session)
    try:
        logging.info("Запуск бота...")
        await dp.start_polling(bot)
    finally:
        logging.info("Остановка бота...")
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
