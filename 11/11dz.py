import os
import re
import textwrap
from collections import defaultdict
from pprint import pprint

import requests
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

try:
    from google.colab import userdata
    os.environ["PROXYAPI_KEY"] = userdata.get('PROXYAPI_KEY')
except Exception as e:
    from dotenv import load_dotenv
    load_dotenv()

# функция для загрузки документа по ссылке из гугл драйв
def load_document_text(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def find_splitters(src_text):
    # поиск типов разделителей
    splitters = defaultdict(int)
    splitter = ""
    for sym in src_text:
        if ord(sym) <= 32:
            splitter += sym
        else:
            splitters[splitter] += 1
            splitter = ""
    pprint(splitters)

def get_chunk_lens(chunks):
    lens = []
    for chu in chunks:
        lens.append(len(chu))
    print(sorted(lens))

def get_faiss_db():
    embeddings = OpenAIEmbeddings(
        api_key=token,
        base_url="https://api.proxyapi.ru/openai/v1"
    )
    try:
        db = FAISS.load_local("./11/faiss_db.index", embeddings, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        print(str(e))
    src_text = load_document_text("https://docs.google.com/document/d/1YhUEX9fZDNTeE3eJ-yXskxZG46LsTRYvXjZ9Ij-t3Gw/export?format=txt")
    # with open("11/tech_reglament.txt", "r") as f:
        # src_data = f.read()
    # find_splitters(src_text)
    splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\r\n\t",
            "\r\n \r\n\r\n\r\n\t \r\n",
            "\r\n \r\n \r\n \r\n \r\n \r\n",
            "\r\n \r\n",
            "\r\n"
        ],
        chunk_size=10,
        chunk_overlap=0
    )
    chunks = splitter.split_text(src_text)
    # get_chunk_lens(chunks)

    source_chunks = []
    for chunk in chunks:
        source_chunks.append(Document(page_content=chunk, metadata={"meta":"data"}))

    # Создадим индексную базу из разделенных фрагментов текста
    db = FAISS.from_documents(source_chunks, embeddings)
    db.save_local("./11/faiss_db.index")
    return db

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


# Обновленная функция взаимодействия с индексной базой, OpenAI и историей переписки
def answer_index_history(
        client, system, query, history, db_index, model="gpt-4o-mini", verbose=False
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


if __name__ == "__main__":
    token = os.environ.get('PROXYAPI_KEY')
    client = OpenAI(
        api_key=token,
        base_url="https://api.proxyapi.ru/openai/v1"
    )

    history = ""
    system = "Ты сотрудник Росстандарта, ответь на вопрос пользователя на основе документа. " \
        "Не придумывай ничего от себя, отвечай максимально по документу. " \
        "Не упоминай Документ при ответе клиенту. Клиент ничего не должен знать про Документ"
    db = get_faiss_db()
    while True:
        query = input('Вопрос пользователя: ')
        # выход из цикла, если пользователь ввел: 'стоп'
        if query == 'стоп': break
        # ответ от OpenAI
        answer = answer_index_history(client, system, query, history, db)
        print(f'Ответ:\n{format_text(answer)}\n')
        # Запись истории диалога
        history += f'Вопрос пользователя: {query}. \nОтвет: {answer}\n'
