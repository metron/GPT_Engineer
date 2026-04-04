import os
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

last_motivations = []

# Запрос к OpenAI
async def get_gpt_motivation_message(model='gpt-4o-mini', temp=0.1):
    messages = [{
        "role": "system", "content": "Ты - изобретатель креативных, мотивирующих девизов."
        }, {
        "role": "user", "content": f"""
            Выдай мотивирующий девиз дня для маркетолога или менеджера по продажам.
            Одно предложение, ничего больше.
            Например: "Ты сможешь закрыть эту сделку!", "Каждая сделка — это шаг к успеху!".
            Не повторяй те девизы, которые ты уже говорил: {"; ".join(last_motivations)}
        """
        }
    ]
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp)
    res = response.choices[0].message.content
    last_motivations.append(res)
    return res
