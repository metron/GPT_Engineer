from openai import OpenAI


client = OpenAI(
    api_key="sk-rn7y6g6yiBuBQut2dCX8Pb7rzL5Lmtr2",
    base_url="https://api.proxyapi.ru/openai/v1",
)

completion_tokens = prompt_tokens = total_tokens = 0    

def get_answer(query: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "user", "content": query}
        ]
    )
    print(f"Ответ: {completion.choices[0].message.content}")

    completion_tokens += completion.usage.completion_tokens
    prompt_tokens += completion.usage.prompt_tokens
    total_tokens += completion.usage.total_tokens
    print(
        f"Использовано токенов: на вопросы: {prompt_tokens}, "
        "на ответы: {completion_tokens}, всего: {total_tokens}"
    )

while True:
    query = input("Ваш вопрос: ")
    if query.lower() == "стоп":
        break
