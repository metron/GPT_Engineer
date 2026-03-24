import csv
import getpass
import json
import os
import re
import textwrap
from datetime import datetime
from io import BytesIO

import docx
import openai
import requests
from langchain_classic.schema import Document
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

try:
    from google.colab import drive, userdata
    os.environ["PROXYAPI_KEY"] = userdata.get('PROXYAPI_KEY')
    drive.mount('/content/drive')
    folder_path = '/content/drive/MyDrive/GPT_Engineer/14'
except Exception as e:
    from dotenv import load_dotenv
    load_dotenv()
    folder_path = os.path.join(os.getcwd(), '14')

# токен доступа к API
token = os.environ.get('PROXYAPI_KEY')

embeddings = OpenAIEmbeddings(
    api_key=token,
    base_url="https://api.proxyapi.ru/openai/v1"
)

# функция для загрузки документа по ссылке из гугл драйв
def load_document_text(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

splitter = RecursiveCharacterTextSplitter(
    separators=[
        "Имя:",
        "\r\n \r\n"
    ],
    chunk_size=100,
    chunk_overlap=0
)

def split_text(text):
    chunks = {}
    # find_splitters(src_text)
    match0 = re.search(r"--- .* ---", text)
    text = text[match0.end():]
    while match1 := re.search(r"--- .* ---", text):
        chunks[match0.group()] = splitter.split_text(text[:match1.end()])
        text = text[match1.end():]
        match0 = match1
        # print(chunks)
    chunks[match0.group()] = splitter.split_text(text)
    # print(chunks)
    # print("-----------------")
    # get_chunk_lens(chunks)
    return chunks

def create_db(chunks):
    source_chunks = []
    for header, chunk in chunks.items():
        source_chunks.append(Document(page_content=chunk, metadata={"header": header}))

    # Создадим индексную базу из разделенных фрагментов текста
    db = FAISS.from_documents(source_chunks, embeddings)
    return db


if __name__ == "__main__":
    # text = load_document_text('https://docs.google.com/document/d/1-0RxQ24upk6_HzazmMbAhcdzvmSvBeE0/export?format=txt')
    text = """
--- Мастера маникюра ---
Имя: Анна
Специализация: гель-лак, дизайн, укрепление ногтей
Цены: маникюр – 1800₽, дизайн +500₽
Особое: работа с хрупкими ногтями
 
Имя: Елена
Специализация: аппаратный педикюр, SPA-уход
Цены: педикюр – 2200₽, SPA +800₽
Особое: медицинские технологии
 
Имя: Ксения
Специализация: бразильский маникюр, френч
Цены: маникюр – 2000₽, френч +300₽
Особое: сложный дизайн
 
--- Парикмахеры ---
Имя: Мария
Специализация: окрашивание, укладки, кератин
Цены: стрижка – 2500₽, окрашивание от 3500₽
Особое: колорист премиум-класса
 
Имя: Алексей
Специализация: мужские стрижки, борода
Цены: стрижка – 2000₽, борода – 1500₽
Особое: стиль barber shop
 
Имя: София
Специализация: длинные волосы, плетение
Цены: укладка – 1800₽, плетение от 2500₽
Особое: свадебные прически
 
--- Универсальные мастера ---
Имя: Виктория
Специализация: маникюр + педикюр (комбо)
Цены: комбо – 3500₽ (вместо 4000₽)
 
Имя: Дарья
Специализация: стрижка + макияж
Цены: пакет – 4000₽ (вместо 4500₽)
 
--- Правила использования ---
1. При записи сначала уточняйте услугу, затем предлагайте мастеров.
2. Акции:
   - При записи к Виктории (маникюр+педикюр) – скидка 15%.
   - Первый визит к Алексею – бесплатная коррекция через 2 недели.
 """
    chunks = split_text(text)
    # print(chunks)
    index_name = f"beauty_salon"
    if not os.path.exists(os.path.join(folder_path, index_name) + ".faiss"):
        db = create_db(chunks)
        db.save_local(folder_path=folder_path, index_name=index_name)
    else:
        db = FAISS.load_local(
            folder_path, embeddings, index_name, allow_dangerous_deserialization=True
        )

