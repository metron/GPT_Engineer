from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from assistant_core.assistant_engine import run_assistant


SESSION_HISTORY_KEY: str = "assistant_history"


@require_http_methods(["GET", "POST"])
def assistant_index(request):
    history: str = request.session.get(SESSION_HISTORY_KEY, "")
    question: str = ""
    answer: str = ""
    error_message: str = ""

    if request.method == "POST" and request.POST.get("action") == "clear_history":
        request.session[SESSION_HISTORY_KEY] = ""
        request.session.modified = True

        return render(
            request=request,
            template_name="assistant_app/index.html",
            context={
                "question": "",
                "answer": "",
                "history": "",
                "error_message": "",
            },
        )

    if request.method == "POST":
        question = (request.POST.get("question") or "").strip()

        if not question:
            error_message = "Пожалуйста, введите вопрос."
        else:
            try:
                answer = run_assistant(question=question, history=history)
            except Exception as e:
                print(str(e))
                answer = ""
                error_message = "Произошла ошибка при обработке запроса. Попробуйте ещё раз."

            if answer and not error_message:
                block = f"Вопрос: {question}\nОтвет: {answer}\n\n"

                new_history = (history + block)[-8000:]

                request.session[SESSION_HISTORY_KEY] = new_history
                request.session.modified = True

                history = new_history

    lower_answer = (answer or "").lower()
    if "не задан api-ключ" in lower_answer:
        error_message = "Не задан API-ключ. Проверьте OPENAI_API_KEY в .env и перезапустите сервер."
        answer = ""
    elif "временно недоступен" in lower_answer:
        error_message = "LLM временно недоступна. Попробуйте ещё раз позже."
        answer = ""
    elif "индекс" in lower_answer and "не найден" in lower_answer:
        error_message = "Не найден индекс базы знаний. Проверьте Шаг 4 (FAISS) и попробуйте пересоздать индекс."
        answer = ""

    return render(
        request=request,
        template_name="assistant_app/index.html",
        context={
            "question": question,
            "answer": answer,
            "history": history,
            "error_message": error_message,
        },
    )