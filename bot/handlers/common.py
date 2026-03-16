from aiogram import Router, types
from aiogram.filters import Command
from bot.services.nlp import get_psychological_response
from bot.utils.history import dialog_history
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """Возвращает клавиатуру с основными командами."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start"), KeyboardButton(text="/info")]
        ],
        resize_keyboard=True,        # подгоняет размер под экран
        one_time_keyboard=False,     # клавиатура остаётся после нажатия
        input_field_placeholder="Выберите команду или напишите сообщение..."
    )
    return keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    dialog_history.clear_history(user_id)  # очищаем историю для нового диалога
    await message.reply(
        "Привет! Я бот психологической поддержки. Напиши мне, что тебя беспокоит.\n\n",
        reply_markup=get_main_keyboard()
    )
    
@router.message(Command("info"))
async def cmd_info(message: types.Message):
    info_text = (
        "📞 **Службы психологической помощи в Зеленограде:**\n\n"
        "• Филиал МСППН (корп. 418)\n"
        "  Телефон: +7 499 735-22-24, 051\n\n"
        "• Экстренная помощь:\n"
        "  - 112 (единый номер экстренных служб)\n"
        "  - 8-800-2000-122 (детский телефон доверия)\n"
        "  - 8 (495) 989-50-50 (МЧС)\n\n"
        "Если тебе нужна срочная помощь, пожалуйста, обратись по этим номерам."
    )
    await message.reply(
        info_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()  # возвращаем клавиатуру
    )
    
@router.message()
async def handle_message(message: types.Message):
    text = message.text
    user_id = message.from_user.id
    if not text:
        await message.reply("Пожалуйста, напиши текстовое сообщение.")
        return

    # Получаем историю пользователя
    history = dialog_history.get_history(user_id)

    try:
        # Генерируем ответ с учётом истории
        reply = get_psychological_response(text, history=history)  # нужно модифицировать функцию
    except Exception as e:
        reply = f"Извини, произошла ошибка: {e}"
    else:
        # Сохраняем диалог в историю
        dialog_history.add_message(user_id, text, reply)

    await message.reply(reply)