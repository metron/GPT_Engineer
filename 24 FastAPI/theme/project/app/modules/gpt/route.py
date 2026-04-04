# app/modules/gpt/route.py

"""
Маршруты для работы с LLM (GPT-модели).

Назначение:
1. Приём POST-запросов с текстом prompt
2. Проверка авторизации пользователя
3. Асинхронный вызов GPT через service.py
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.route import get_current_user  # проверка авторизации
from app.modules.gpt.schema import GPTRequest, GPTResponse
from app.modules.gpt.service import call_gpt

router = APIRouter(prefix="/gpt", tags=["gpt"])

@router.post("/", response_model=GPTResponse, status_code=status.HTTP_200_OK)
async def gpt_endpoint(request: GPTRequest, current_user=Depends(get_current_user)):
    """
    POST /gpt
    Асинхронно вызывает GPT-модель и возвращает ответ.
    Требует авторизации пользователя.
    """
    try:
        answer = await call_gpt(
            prompt=f"""{request.prompt}\nТекущая дата: {datetime.now().strftime("%Y-%m-%d")}""",
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при вызове LLM: {str(e)}"
        )
