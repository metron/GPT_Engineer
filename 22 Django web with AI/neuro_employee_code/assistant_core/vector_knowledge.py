import os
from pathlib import Path
from functools import lru_cache
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


BASE_DIR: Path = Path(__file__).resolve().parent
KB_TEXT_PATH: Path = BASE_DIR / "kb" / "knowledge_base.txt"
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
    embeddings_model = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=embeddings_model)


def build_and_save_faiss_index() -> FAISS:
    kb_text = _load_kb_text()

    documents = _split_text_to_documents(kb_text)

    embeddings = _build_embeddings()
    db_index = FAISS.from_documents(documents, embeddings)

    FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    db_index.save_local(str(FAISS_INDEX_DIR))

    return db_index


@lru_cache(maxsize=1)
def get_db_index() -> FAISS:
    embeddings = _build_embeddings()
    if FAISS_INDEX_DIR.exists():
        return FAISS.load_local(
            str(FAISS_INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    return build_and_save_faiss_index()


def find_relevant_snippets(query: str, k: int = 4) -> str:
    db_index = get_db_index()
    docs = db_index.similarity_search(query, k=k)
    snippets: list[str] = []
    for doc in docs:
        snippets.append(doc.page_content.strip())

    return "\n\n---\n\n".join(snippets)