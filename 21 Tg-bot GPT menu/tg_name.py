import asyncio
import aiogram
from aiogram import Bot

async def main():
  bot = Bot(token='7136704227:AAEsBccdQMOzoLm6TKyL9LgsWOCycJ6TVts')
  # ID пользователя (число)
  user_id = 7136704227
  chat = await bot.get_chat(user_id)
  print(chat.username)  # username
  print(chat.first_name) # Имя

if __name__ == "__main__":
  asyncio.run(main())