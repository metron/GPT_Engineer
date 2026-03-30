import os

import re
import textwrap
import requests
from dotenv import load_dotenv
from .vector_knowledge import get_db_index


load_dotenv()


DEFAULT_SYSTEM_PROMPT: str = (
    "Ты — консультант компании Simble. Отвечай на вопрос клиента строго на основе документа с информацией. "
    "Не придумывай факты от себя. "
    "Не упоминай документ, отрывки и внутренние источники в ответе. "
    "Если в документе нет ответа — скажи честно и предложи, что уточнить."
)


def format_text(text: str, width: int = 120) -> str:
    paragraphs = text.split("\n")

    formatted_paragraphs: list[str] = []
    for paragraph in paragraphs:
        formatted_paragraphs.append(textwrap.fill(paragraph, width))

    return "\n".join(formatted_paragraphs)


def _build_message_content(query: str, db_index, k: int = 5) -> str:
    docs = db_index.similarity_search(query, k=k)

    raw_blocks = []
    for i, doc in enumerate(docs):
        raw_blocks.append(f"\nОтрывок документа №{i + 1}\n{doc.page_content}\n")

    message_content = "\n ".join(raw_blocks)

    message_content = re.sub(r"\n{2,}", " ", message_content)

    return message_content


def _call_llm(messages: list[dict], model: str, temperature: float = 0.0) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    api_base = os.getenv("OPENAI_API_BASE", "https://api.proxyapi.ru/openai/v1").strip()

    if not api_key or api_key == "PASTE_YOUR_PROXYAPI_KEY_HERE":
        return "Не задан API-ключ. Укажите OPENAI_API_KEY в .env и перезапустите сервер."

    url = f"{api_base.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.RequestException:
        return "Сервис LLM временно недоступен. Попробуйте ещё раз позже."

    except (KeyError, IndexError, ValueError):
        return "Не удалось разобрать ответ модели. Попробуйте ещё раз позже."


def answer_index_history(
    system: str,
    query: str,
    history: str,
    db_index,
    model: str = "gpt-4o-mini",
    verbose: bool = False,
) -> str:
    message_content = _build_message_content(query=query, db_index=db_index, k=5)

    if verbose:
        print("\n\n", message_content)

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                "Ответь на вопрос клиента. Не упоминай документ с информацией для ответа клиенту в ответе.\n"
                f"Документ с информацией для ответа клиенту:\n\n{message_content}\n\n"
                f"История диалога:\n{history}\n\n"
                f"Вопрос клиента:\n{query}"
            ),
        },
    ]

    return _call_llm(messages=messages, model=model, temperature=0.0)


def run_assistant(question: str, history: str) -> str:
    question_clean = (question or "").strip()
    if not question_clean:
        return "Пожалуйста, напишите вопрос."

    max_chars = int(os.getenv("MAX_QUESTION_CHARS", "2000"))
    if len(question_clean) > max_chars:
        return f"Слишком длинный вопрос. Сократите до {max_chars} символов."

    db_index = get_db_index()

    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    answer = answer_index_history(
        system=DEFAULT_SYSTEM_PROMPT,
        query=question_clean,
        history=history or "",
        db_index=db_index,
        model=model,
        verbose=False,
    )

    return answer.strip()