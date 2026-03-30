from openai import OpenAI
import os


try:
    from google.colab import userdata
    os.environ["PROXYAPI_KEY"] = userdata.get('PROXYAPI_KEY')
except Exception as e:
    from dotenv import load_dotenv
    load_dotenv()

token = os.environ.get('PROXYAPI_KEY')

client = OpenAI(
    api_key=token,
    base_url="https://api.proxyapi.ru/openai/v1"
)

completion_tokens, prompt_tokens, total_tokens = 0, 0, 0

def get_answer(query: str):
    global completion_tokens, prompt_tokens, total_tokens
    completion = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "user", "content": query}
        ]
    )
    completion_tokens += completion.usage.completion_tokens
    prompt_tokens += completion.usage.prompt_tokens
    total_tokens += completion.usage.total_tokens
    print(
        f"Использовано токенов: на вопросы: {prompt_tokens}, "
        f"на ответы: {completion_tokens}, всего: {total_tokens}"
    )
    return completion.choices[0].message.content


while True:
    query = input("Ваш вопрос: ")
    if query.lower() == "стоп":
        break
    print(f"Ответ: {get_answer(query)}")
