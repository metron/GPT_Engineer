import os
import textwrap
from collections import defaultdict
from pprint import pprint

import requests
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import \
    create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from google.colab import drive, userdata
    os.environ["PROXYAPI_KEY"] = userdata.get('PROXYAPI_KEY')
    drive.mount('/content/drive')
    folder_path = '/content/drive/MyDrive/GPT_Engineer/12'
except Exception as e:
    from dotenv import load_dotenv
    load_dotenv()
    folder_path = os.path.join(os.getcwd(), '12')

# токен доступа к API
token = os.environ.get('PROXYAPI_KEY')
# База знаний компании Simble - часть 1 (без разбивки MarkDown)
data_urls = [
    'https://docs.google.com/document/d/1Z7eZLIPG9URgOFz-yqtJAup-WXhKFIiF/export?format=txt',
    'https://docs.google.com/document/d/1qxJXwHtYNxx6ecf35zhqFYBxSjoA5Mhr/export?format=txt'
]
embeddings = OpenAIEmbeddings(
    api_key=token,
    base_url="https://api.proxyapi.ru/openai/v1"
)

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

def find_splitters(src_text):
    # поиск типов разделителей
    splitters = defaultdict(int)
    splitter = ""
    for sym in src_text:
        if ord(sym) <= 32 or ord(sym) == 92:
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

# функция для загрузки документа по ссылке из гугл драйв
def load_document_text(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def create_db(url_text):
    src_text = load_document_text(url_text)
    # find_splitters(src_text)
    splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\r\n\r\n\r\n",
            "\r\n",
            "\\"
        ],
        chunk_size=100,
        chunk_overlap=0
    )
    chunks = splitter.split_text(src_text)
    # get_chunk_lens(chunks)
    source_chunks = []
    for chunk in chunks:
        source_chunks.append(Document(page_content=chunk, metadata={"meta":"data"}))

    # Создадим индексную базу из разделенных фрагментов текста
    db = FAISS.from_documents(source_chunks, embeddings)
    return db

# Обернем в функцию
# Создание цепочки модели с использованием ретривера для поиска по векторной базе данных
def create_model_chain(
    db_index, # векторная база знаний
    k=3,      # используемое к-во чанков
    model='gpt-4o-mini',
    temp=0.1
):
    llm = ChatOpenAI(
        model=model,
        temperature=temp,
        api_key=token,
        base_url="https://api.proxyapi.ru/openai/v1"
    )
    retriever = db_index.as_retriever(search_type="similarity", search_kwargs={"k": k})
    system_prompt = """
        Ответь на вопрос пользователя используя отрезки текста.
        Context: {context}
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt), ("human", "{input}")
    ])

    return create_retrieval_chain(
        retriever,
        create_stuff_documents_chain(llm, prompt)
    )

if __name__ == "__main__":
    for i in range(2):
        index_name = f"simble_{i}"
        if not os.path.exists(os.path.join(folder_path, index_name) + ".faiss"):
            db = create_db(data_urls[i])
            db.save_local(folder_path=folder_path, index_name=index_name)

    dbs = []
    for i in range(2):
        dbs.append(FAISS.load_local(
            folder_path, embeddings, f"simble_{i}", allow_dangerous_deserialization=True
        ))

    dbs[0].merge_from(dbs[1])
    db_merged = dbs[0]

    new_chain = create_model_chain(db_merged)

    query = "Интересные факты о маркетинге социальных сетей"
    ans = new_chain.invoke({"input": query})

    print('Ответ модели:\n')
    print(format_text(ans['answer']), '\n')
