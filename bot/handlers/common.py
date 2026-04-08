from aiogram import Router, types
from aiogram.filters import Command
from bot.services.nlp import get_psychological_response
from bot.utils.history import dialog_history
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.services.recommender import get_recommendations, format_recommendations
from bot.services.nlp import classify_state
from bot.utils.logger import handlers_logger
from bot.utils.helpers import contains_keywords, BOOK_KEYWORDS, MOVIE_KEYWORDS


def get_main_keyboard():
    """Возвращает клавиатуру с основными командами."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/start"), KeyboardButton(text="/info")]],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите команду или напишите сообщение...",
    )
    return keyboard


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    handlers_logger.info(f"User {user_id} executed /start")
    dialog_history.clear_history(user_id)
    await message.reply(
        "Привет! Я бот психологической поддержки. Напиши мне, что тебя беспокоит.\n\n"
        "Доступные команды:\n"
        "/help — справка о боте\n"
        "/info — службы помощи\n"
        "/start — начать новый диалог",
        reply_markup=get_main_keyboard(),
    )
    handlers_logger.debug(f"Start command handled for user {user_id}")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    user_id = message.from_user.id
    handlers_logger.info(f"User {user_id} executed /help")
    help_text = (
        "🧠 **Твой психолог — справка**\n\n"
        "Я бот для психологической поддержки и помощи в стрессовых ситуациях.\n\n"
        "**Что я умею:**\n"
        "• Выслушаю и поддержу в трудную минуту\n"
        "• Помогу разобраться в эмоциях\n"
        "• Предложу техники самопомощи\n"
        "• Порекомендую книги и упражнения\n\n"
        "**Команды:**\n"
        "/start — начать новый диалог\n"
        "/help — эта справка\n"
        "/info — телефоны служб помощи\n\n"
        "**Важно:**\n"
        "Я не заменяю профессионального психолога. "
        "Если тебе нужна срочная помощь, используй команду /info"
    )
    await message.reply(
        help_text, parse_mode="Markdown", reply_markup=get_main_keyboard()
    )
    handlers_logger.debug(f"Help sent to user {user_id}")


@router.message(Command("info"))
async def cmd_info(message: types.Message):
    user_id = message.from_user.id
    handlers_logger.info(f"User {user_id} requested /info (emergency contacts)")
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
        reply_markup=get_main_keyboard(),
    )
    handlers_logger.debug(f"Emergency contacts sent to user {user_id}")


@router.message()
async def handle_message(message: types.Message):
    text = message.text
    user_id = message.from_user.id
    if not text:
        handlers_logger.warning(f"Empty message from user {user_id}")
        await message.reply("Пожалуйста, напиши текстовое сообщение.")
        return

    handlers_logger.info(f"Message from {user_id}: {text[:100]}")

    # --- Блок рекомендаций ---
    # Проверка на запрос книг
    if contains_keywords(text, BOOK_KEYWORDS):
        handlers_logger.info(f"User {user_id} requested book recommendation")
        state = classify_state(text)
        handlers_logger.debug(f"Detected state for books: {state}")
        try:
            results = get_recommendations("book", text, difficulty_name=state, limit=3)
            response = format_recommendations(results, "book")
            await message.reply(response, parse_mode="Markdown")
            handlers_logger.info(
                f"Sent {len(results)} book recommendations to {user_id}"
            )
        except Exception as e:
            handlers_logger.error(
                f"Error getting book recommendations for {user_id}: {e}", exc_info=True
            )
            await message.reply(
                "Извините, не удалось найти рекомендации. Попробуйте позже."
            )
        return

    # Проверка на запрос фильмов/сериалов
    if contains_keywords(text, MOVIE_KEYWORDS):
        handlers_logger.info(f"User {user_id} requested movie recommendation")
        state = classify_state(text)
        handlers_logger.debug(f"Detected state for movies: {state}")
        try:
            results = get_recommendations("movie", text, difficulty_name=state, limit=3)
            response = format_recommendations(results, "movie")
            await message.reply(response, parse_mode="Markdown")
            handlers_logger.info(
                f"Sent {len(results)} movie recommendations to {user_id}"
            )
        except Exception as e:
            handlers_logger.error(
                f"Error getting movie recommendations for {user_id}: {e}", exc_info=True
            )
            await message.reply(
                "Извините, не удалось найти рекомендации. Попробуйте позже."
            )
        return
    # --- Конец блока рекомендаций ---

    # Обычный диалог с нейросетью
    history = dialog_history.get_history(user_id)
    handlers_logger.debug(f"History length for user {user_id}: {len(history)}")

    try:
        reply = get_psychological_response(text, history=history)
        handlers_logger.debug(f"Generated response for {user_id}: {reply[:100]}")
    except Exception as e:
        handlers_logger.error(
            f"Error generating response for {user_id}: {e}", exc_info=True
        )
        reply = "Извини, произошла ошибка. Пожалуйста, попробуй ещё раз."
    else:
        dialog_history.add_message(user_id, text, reply)
        handlers_logger.debug(
            f"Dialog history updated for {user_id}, new length: {len(dialog_history.get_history(user_id))}"
        )

    await message.reply(reply)
    handlers_logger.info(f"Response sent to user {user_id}")
