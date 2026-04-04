from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


# Функция создания Reply-клавиатуры
async def create_reply_keyboard():
    kb = [
        [
            KeyboardButton(text="Добавить задачу"),
            KeyboardButton(text="Добавить сделку"),
        ],[
            KeyboardButton(text="Просмотреть задачи"),
            KeyboardButton(text="Просмотреть сделки"),
        ],[
            KeyboardButton(text="Получить мотивацию"),
            KeyboardButton(text="Стоп"),
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
