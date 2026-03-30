import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR: Path = Path(__file__).resolve().parent
KB_TEXT_PATH: Path = BASE_DIR / "kb" / "knowledge_base.txt"
KB_CONF_PATH: Path = BASE_DIR / "kb" / "kb_conf.json"
FAISS_INDEX_DIR: Path = BASE_DIR / "kb" / "faiss_index"


def _load_kb_text() -> str:
    return KB_TEXT_PATH.read_text(encoding="utf-8")


def _split_text_to_documents(text: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=0,
    )
    chunks = splitter.split_text(text)
    documents: list[Document] = []
    for chunk in chunks:
        documents.append(Document(page_content=chunk, metadata={"source": "knowledge_base"}))

    return documents


def _build_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        model=os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
    )


def build_and_save_faiss_index() -> FAISS:
    kb_text = _load_kb_text()

    documents = _split_text_to_documents(kb_text)

    embeddings = _build_embeddings()
    db_index = FAISS.from_documents(documents, embeddings)

    FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    db_index.save_local(str(FAISS_INDEX_DIR))

    return db_index


def check_hash_changed(file_path):
    hash_obj = hashlib.sha256()
    with open(str(KB_TEXT_PATH), "rb") as f:
        hash_obj.update(f.read())
        kb_hash = hash_obj.hexdigest()
    if file_path.exists():
        with open(str(file_path), "r") as f:
            kb_conf = json.load(f)
        if kb_conf[KB_TEXT_PATH.name] == kb_hash:
            print("check_hash_changed - False")
            return False

    with open(str(file_path), "w") as f:
        kb_conf = {KB_TEXT_PATH.name: kb_hash}
        json.dump(kb_conf, f)
    print("check_hash_changed - True")
    return True


def get_db_index() -> FAISS:
    if FAISS_INDEX_DIR.exists() and not check_hash_changed(KB_CONF_PATH):
        embeddings = _build_embeddings()
        return FAISS.load_local(
            str(FAISS_INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    return build_and_save_faiss_index()
