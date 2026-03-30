import os
import re
import textwrap
from collections import defaultdict

import openai
import requests
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

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

# функция для загрузки документа по ссылке из гугл драйв
def load_document_text(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

data_from_url = load_document_text("https://docs.google.com/document/d/1q4l912Re8zuIfBax4FDS3ZppYmVPzER3Si2wrmznddc/export?format=txt")
chunks = re.split(r" \d+\. ", data_from_url)
source_chunks = []
freq = []
for chunk in chunks:
    if len(chunk) > 1000:
        chs = re.split(r"\. ", chunk)
        for ch in chs:
            freq.append(len(ch))
            source_chunks.append(Document(page_content=ch, metadata={"meta":"data"}))
    else:
        freq.append(len(chunk))
        source_chunks.append(Document(page_content=chunk, metadata={"meta":"data"}))

# print(sorted(freq))
embeddings = OpenAIEmbeddings(
    api_key=token,
    base_url="https://api.proxyapi.ru/openai/v1"
)
# Создадим индексную базу из разделенных фрагментов текста
db = FAISS.from_documents(source_chunks, embeddings)

# Функция для форматирования текста по абзацам
def format_text(text, width=120):
    # Разделяем текст на абзацы
    paragraphs = text.split('\n')
    # Форматируем каждый абзац отдельно
    formatted_paragraphs = []
    for paragraph in paragraphs:
        # Используем textwrap.fill для форматирования абзаца, чтобы длина строки не превышала width
        formatted_paragraph = textwrap.fill(paragraph, width)
        formatted_paragraphs.append(formatted_paragraph)
    # Объединяем абзацы с символом новой строки
    return '\n'.join(formatted_paragraphs)


def answer_index(system, topic, search_index, verbose=True):
    # Поиск релевантных отрезков из базы знаний
    docs = search_index.similarity_search(topic, k=4)
    if verbose: print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join(
        [f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if verbose: print('message_content :\n ======================================== \n', message_content)
    client = OpenAI()
    messages = [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Ответь на вопрос клиента. Не упоминай документ с информацией для ответа клиенту \
         в ответе. Документ с информацией для ответа клиенту: {message_content} \
         \n\nВопрос клиента: \n{topic}"}
    ]
    if verbose: print('\n ===========================================: ')
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0
    )
    answer = completion.choices[0].message.content
    return answer  # возвращает ответ

# Обновленная функция взаимодействия с индексной базой, OpenAI и историей переписки
def answer_index_history(
        system, query, history, db_index, model="gpt-4o-mini", verbose=False
    ):
    # Поиск релевантных отрезков из базы знаний
    docs = db_index.similarity_search(query, k=5)
    message_content = re.sub(r'\n{2}', ' ', '\n '.join(
        [f'\nОтрывок документа №{i+1}\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if verbose: print('\n\n', message_content)
    messages = [
        {"role": "system", "content": system},
        {"role": "user",
         "content":
         f"Ответь на вопрос клиента. Не упоминай документ с информацией для ответа клиенту в ответе. \
         Документ с информацией для ответа клиенту: \n\n{message_content} \
         \n\nИстория диалога: \n{history} \
         \n\nВопрос клиента: \n{query}"}
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return completion.choices[0].message.content # возвращает ответ

history = ""
system = "Ты инженер по промышленной безопасности, ты специалист по охране труда, ответь на вопрос пользователя на основе документа с информацией. \
Не придумывай ничего от себя, отвечай максимально по документу. Не упоминай Документ с информацией для \
ответа клиенту. Клиент ничего не должен знать про Документ с информацией для ответа клиенту"
while True:
    query = input('Вопрос пользователя: ')
    # выход из цикла, если пользователь ввел: 'стоп'
    if query == 'стоп': break
    # ответ от OpenAI
    answer = answer_index_history(system, query, history, db)
    print(f'Ответ:\n{format_text(answer)}\n')
    # Запись истории диалога
    history += f'Вопрос пользователя: {query}. \nОтвет: {answer}\n'
