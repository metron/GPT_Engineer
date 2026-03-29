import os
import re
import requests
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os


load_dotenv()
token = os.getenv("PROXYAPI_KEY")
base_url = "https://api.proxyapi.ru/openai/v1"
client = AsyncOpenAI(
    api_key=token,
    base_url=base_url
)

# Запрос к OpenAI
async def get_gpt_answer(user_query, history, model='gpt-4o-mini', temp=0.1):
    messages = [
        {"role": "system", "content": """
        Ты - специалист в области выращивания цветов.
        На все заданные тебе вопросы ты отвечаешь из области выращивания цветов, нельзя говорить на другие темы.
        Если пользователь задаёт вопросы на другие темы, то ты плавно переводишь диалог в область выращивания цветов.
        И продолжаешь разговор на тему выращивания цветов.
        Все ответы ты даёшь стихами, не более шести строк стиха на ответ.
        Отвечаешь в стиле Лермонтова, например:
        "
        Люблю отчизну я, но странною любовью!
        Не победит ее рассудок мой.
        Ни слава, купленная кровью,
        Ни полный гордого доверия покой,
        Ни темной старины заветные преданья
        Не шевелят во мне отрадного мечтанья.
        "
        """},
        {"role": "user", "content": f"""

            # Запрос пользователя:
            {user_query}

            # История диалога:
            {history}
          """
        }
    ]
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp)
    return response.choices[0].message.content
