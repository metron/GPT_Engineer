from openai import OpenAI

client = OpenAI(
    api_key="sk-rn7y6g6yiBuBQut2dCX8Pb7rzL5Lmtr2",
    base_url="https://api.proxyapi.ru/openai/v1",
)

response = client.responses.create(
    model="gpt-4o-mini", 
    input="Привет!"
)

print(response.output_text)
