from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommand, CallbackQuery, InlineKeyboardMarkup, Message, InlineKeyboardButton
)
from func_base import get_gpt_motivation_message
from keyboards import create_reply_keyboard


router = Router()

class DialogState(StatesGroup):
    add_task_name = State()     # добавление названия задачи
    add_task_term = State()     # добавление срока задачи
    add_deal_name = State()     # добавление названия сделки
    add_deal_sum = State()      # добавление суммы сделки
    add_deal_status = State()   # добавление статуса сделки
    edit_deal_status = State()  # редактирование статуса сделки


# Меню бота
@router.startup()  # Действия, выполняемые при запуске бота
async def on_startup(bot: Bot):
    # Устанавливаем команду /start с пояснением
    main_menu_commands = [
        BotCommand(command='start', description="Запуск бота"),
        BotCommand(command='clear_history', description="Очистка истории")
   ]   
    await bot.set_my_commands(main_menu_commands)

# Обработчик команды "Стоп"
@router.message(F.text == "Стоп")
async def stop(message: Message, state: FSMContext):
    await message.answer("Сросил состояние")
    await state.set_state(state=None)
    return


async def check_keyboard_commands(message, state):
    # Проверяем, не хочет ли пользователь вызвать другую функцию
    func = {
        "Добавить задачу": add_task,
        "Добавить сделку": add_deal,
        "Просмотреть задачи": show_tasks,
        "Просмотреть сделки": show_deals,
        "Получить мотивацию": get_motive,
        "Стоп": stop,
    }.get(message.text)
    if func:
        await func(message, state)  # Останавливаем обработку
        return True

# Обработка команды /start
@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
# Сброс текущего состояния
    await state.clear()
    greeting_message = (
        "Здравствуйте! 😊\n"
        "Я ваш помощник по планированию задач, отслеживанию сделок, анализу данных."
        "Я могу давать полезные советы по маркетингу и мотивировать на успех!"
    )
    await message.answer(greeting_message, reply_markup=await create_reply_keyboard())

# Очистка всей истории чата
@router.message(Command('clear_history'))
async def clear_chat_history(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("История диалога очищена. Вы можете начать новый запрос по кнопке внизу экрана.", reply_markup=await create_reply_keyboard())

# Обработчик кнопки "Добавить задачу"
@router.message(F.text == "Добавить задачу")
async def add_task(message: Message, state: FSMContext):
    await state.set_state(DialogState.add_task_name)
    await message.answer("Введите название задачи")

# Обработчик состояния "Добавить имя задачи"
@router.message(DialogState.add_task_name)
async def add_task_name(message: Message, state: FSMContext):
    if await check_keyboard_commands(message, state):
        return
    data = await state.get_data()
    tasks = data.get("tasks", {})  # Получаем список задач из состояния
    next_task_id = data.get("next_task_id", 1) 
    tasks[next_task_id] = {"name": message.text}  # Сохраняем имя задачи
    await state.update_data(tasks=tasks, next_task_id=next_task_id+1)  # Обновляем данные
    await state.set_state(DialogState.add_task_term)
    await message.answer(f"Введите срок выполнения задачи")

# Обработчик состояния "Добавить срок выполнения задачи"
@router.message(DialogState.add_task_term)
async def add_task_name(message: Message, state: FSMContext):
    if await check_keyboard_commands(message, state):
        return
    data = await state.get_data()
    tasks = data["tasks"]  # Получаем список задач из состояния
    next_task_id = data["next_task_id"]
    tasks[next_task_id-1]["term"] = message.text  # Сохраняем срок задачи
    await state.update_data(tasks=tasks)  # Обновляем список задач
    await state.set_state(state=None)
    await message.answer(await get_gpt_motivation_message())

# Обработчик кнопки "Просмотреть задачи"
@router.message(F.text == "Просмотреть задачи")
async def show_tasks(message: Message, state: FSMContext):
    await state.set_state(state=None)
    data = await state.get_data()
    tasks = data.get("tasks", {})  # Получаем список задач из состояния
    if not tasks:
        await message.answer("Нет задач")
    for task_id, task in tasks.items():
        await message.answer(
            f"""Задача: {task["name"]}\nСрок: {task["term"]}""",
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Удалить", callback_data=f"remove_task_{task_id}")],
            ])
        )

# Обработка выбора пункта для удаления задачи
@router.callback_query(F.data.startswith("remove_task_"))
async def remove_task(callback_query: CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[-1])  # Получаем id задачи
    data = await state.get_data()
    tasks = data["tasks"]  # Получаем список задач из состояния
    if tasks.pop(task_id, None):
        await state.update_data(tasks=tasks)  # Сохраняем, какое поле редактируем
        await callback_query.message.answer(f"Задача удалена")
    else:
        await callback_query.message.answer(f"Задача была удалена ранее")
    await state.set_state(state=None)



# Обработчик кнопки "Добавить сделку"
@router.message(F.text == "Добавить сделку")
async def add_deal(message: Message, state: FSMContext):
    await state.set_state(DialogState.add_deal_name)
    await message.answer("Введите название сделки")

# Обработчик состояния "Добавить название сделки"
@router.message(DialogState.add_deal_name)
async def add_deal_name(message: Message, state: FSMContext):
    if await check_keyboard_commands(message, state):
        return
    data = await state.get_data()
    deals = data.get("deals", {})  # Получаем список сделок из состояния
    next_deal_id = data.get("next_deal_id", 1) 
    deals[next_deal_id] = {"name": message.text}  # Сохраняем имя сделки
    await state.update_data(deals=deals, next_deal_id=next_deal_id+1)  # Обновляем данные
    await state.set_state(DialogState.add_deal_sum)
    await message.answer(f"Введите сумму сделки")

# Обработчик состояния "Добавить сумму сделки"
@router.message(DialogState.add_deal_sum)
async def add_deal_sum(message: Message, state: FSMContext):
    if await check_keyboard_commands(message, state):
        return
    data = await state.get_data()
    deals = data["deals"]  # Получаем список сделок из состояния
    next_deal_id = data["next_deal_id"]
    deals[next_deal_id-1]["sum"] = message.text  # Сохраняем сумму сделки
    await state.update_data(deals=deals)  # Обновляем список сделок
    await state.set_state(DialogState.add_deal_status)
    await message.answer(f"Введите статус сделки")

# Обработчик состояния "Добавить статус сделки"
@router.message(DialogState.add_deal_status)
async def add_deal_status(message: Message, state: FSMContext):
    if await check_keyboard_commands(message, state):
        return
    data = await state.get_data()
    deals = data["deals"]  # Получаем список сделок из состояния
    next_deal_id = data["next_deal_id"]
    deals[next_deal_id-1]["status"] = message.text  # Сохраняем статус сделки
    await state.update_data(deals=deals)  # Обновляем список задач
    await state.set_state(state=None)
    await message.answer(f"Сделка создана")

# Обработчик кнопки "Просмотреть сделки"
@router.message(F.text == "Просмотреть сделки")
async def show_deals(message: Message, state: FSMContext, rq_deal_id=None):
    await state.set_state(state=None)
    data = await state.get_data()
    deals = data.get("deals", {})  # Получаем список сделок из состояния
    if not deals:
        await message.answer("Нет сделок")
    for deal_id, deal in deals.items() if rq_deal_id is None else [(rq_deal_id, deals[rq_deal_id])]:
        await message.answer(
            f"""Сделка: {deal["name"]}\nСумма: {deal["sum"]}\nСтатус: {deal["status"]}""",
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Изменить статус",
                    callback_data=f"edit_status_{deal_id}"
                )],
            ])
        )

# Обработка выбора пункта для изменения статуса сделки
@router.callback_query(F.data.startswith("edit_status_"))
async def edit_deal_status(callback_query: CallbackQuery, state: FSMContext):
    edit_deal_id = int(callback_query.data.split("_")[-1])  # Получаем id сделки
    await state.update_data(edit_deal_id=edit_deal_id)  # Сохраняем, какое поле редактируем
    await callback_query.message.answer(f"Введите статус")
    await state.set_state(DialogState.edit_deal_status)

# Обработка ввода нового значения и снова показываем клавиатуру
@router.message(DialogState.edit_deal_status)
async def update_corrected_info(message: Message, state: FSMContext):
    if await check_keyboard_commands(message, state):
        return
    new_value = message.text.strip()
    data = await state.get_data()
    deals = data["deals"]  # Получаем все сделки
    # Обновляем данные
    edit_deal_id = data["edit_deal_id"]
    deals[edit_deal_id]["status"] = new_value
    await state.update_data(deals=deals, edit_deal_id=None)  # и очищаем временные данные
    # Показываем обновлённую информацию
    await message.answer(f"Статус обновлён!")
    await state.set_state(state=None)
    await show_deals(message, state, rq_deal_id=edit_deal_id)

# Обработчик команды "Получить мотивацию"
@router.message(F.text == "Получить мотивацию")
async def get_motive(message: Message):
    await message.answer(await get_gpt_motivation_message())
