from google.colab import userdata
from openai import OpenAI

token = userdata.get("PROXYAPI_KEY")
base_url = "https://api.proxyapi.ru/openai/v1"
client = OpenAI(
    api_key=token,
    base_url=base_url
)