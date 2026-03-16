from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.config import ADMINS
from bot.services.db import (
    get_all_categories,
    get_content_items,
    get_content_by_id,
    add_feedback,
    get_all_stress_types,
)
from bot.keyboards.admin_kb import (
    get_admin_keyboard,
    get_cancel_keyboard,
    get_content_type_keyboard,
    get_stress_type_keyboard,
    get_confirm_keyboard,
)

router = Router()


# ============================================
# Проверка админа
# ============================================

async def is_admin(user_id: int) -> bool:
    """Проверка: является ли пользователь админом"""
    return user_id in ADMINS


async def admin_only(message: types.Message) -> bool:
    """Фильтр только для админов"""
    if not await is_admin(message.from_user.id):
        await message.reply("❌ Доступ запрещён.\n\nТолько администраторы могут использовать эту команду.")
        return False
    return True


# ============================================
# FSM States (состояния для диалогов)
# ============================================

class AdminAddContent(StatesGroup):
    """Состояния для добавления контента"""
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_metadata = State()
    waiting_for_stress_type = State()
    waiting_for_content_text = State()


class AdminEditContent(StatesGroup):
    """Состояния для редактирования контента"""
    waiting_for_content_id = State()
    waiting_for_field = State()
    waiting_for_new_value = State()


class AdminDeleteContent(StatesGroup):
    """Состояния для удаления контента"""
    waiting_for_content_id = State()


# ============================================
# Команды
# ============================================

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Админ-панель (главное меню)"""
    if not await admin_only(message):
        return
    
    await message.reply(
        "🛠️ **Админ-панель**\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard()
    )


@router.message(Command("add_content"))
async def cmd_add_content(message: types.Message, state: FSMContext):
    """Начать добавление контента"""
    if not await admin_only(message):
        return
    
    await message.reply(
        "➕ **Добавление контента**\n\nВыберите категорию:",
        parse_mode="Markdown",
        reply_markup=get_content_type_keyboard()
    )
    await state.set_state(AdminAddContent.waiting_for_category)


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Статистика бота"""
    if not await admin_only(message):
        return
    
    # TODO: Здесь будет реальная статистика из БД
    stats_text = (
        "📊 **Статистика бота**\n\n"
        "👥 Пользователи: 0 (пока нет данных)\n"
        "💬 Сообщений обработано: 0\n"
        "📚 Контент в базе: 0\n"
        "🕒 Аптайм: 0 дней\n\n"
        "_Статистика будет доступна после подключения БД_"
    )
    await message.reply(stats_text, parse_mode="Markdown")


# ============================================
# Callback query handlers (кнопки)
# ============================================

@router.callback_query(F.data == "admin_cancel")
async def on_admin_cancel(callback: types.CallbackQuery, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено")


@router.callback_query(F.data == "admin_add_content")
async def on_admin_add_content(callback: types.CallbackQuery, state: FSMContext):
    """Начать добавление контента"""
    await callback.message.edit_text(
        "➕ **Добавление контента**\n\nВыберите категорию:",
        parse_mode="Markdown",
        reply_markup=get_content_type_keyboard()
    )
    await state.set_state(AdminAddContent.waiting_for_category)


@router.callback_query(F.data.startswith("content_type_"))
async def on_content_type_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбрана категория контента"""
    content_type = callback.data.replace("content_type_", "")
    await state.update_data(content_type=content_type)
    
    await callback.message.edit_text(
        f"✅ Категория: **{content_type}**\n\nВведите **название** контента:",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminAddContent.waiting_for_title)


@router.message(AdminAddContent.waiting_for_title)
async def on_title_received(message: types.Message, state: FSMContext):
    """Получено название контента"""
    await state.update_data(title=message.text)
    
    await message.reply(
        f"✅ Название: **{message.text}**\n\nВведите **описание**:",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminAddContent.waiting_for_description)


@router.message(AdminAddContent.waiting_for_description)
async def on_description_received(message: types.Message, state: FSMContext):
    """Получено описание контента"""
    await state.update_data(description=message.text)
    
    await message.reply(
        f"✅ Описание сохранено.\n\nВведите **метаданные** (автор, платформа и т.д.) в формате JSON:\n"
        f"_(или отправьте `-` чтобы пропустить)_",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminAddContent.waiting_for_metadata)


@router.message(AdminAddContent.waiting_for_metadata)
async def on_metadata_received(message: types.Message, state: FSMContext):
    """Получены метаданные"""
    metadata = message.text
    if metadata == "-":
        metadata = {}
    else:
        # Простая парсинг JSON (в продакшене нужна валидация)
        try:
            import json
            metadata = json.loads(metadata)
        except:
            metadata = {"raw": metadata}
    
    await state.update_data(metadata=metadata)
    
    await message.reply(
        "✅ Метаданные сохранены.\n\nВыберите **тип стресса**:",
        reply_markup=get_stress_type_keyboard()
    )
    await state.set_state(AdminAddContent.waiting_for_stress_type)


@router.callback_query(F.data.startswith("stress_"))
async def on_stress_type_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбран тип стресса"""
    stress_type = callback.data.replace("stress_", "")
    await state.update_data(stress_type=stress_type)
    
    await callback.message.edit_text(
        f"✅ Тип стресса: **{stress_type}**\n\n"
        f"Введите **текст контента** (техника, упражнение) или `-` чтобы пропустить:",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminAddContent.waiting_for_content_text)


@router.message(AdminAddContent.waiting_for_content_text)
async def on_content_text_received(message: types.Message, state: FSMContext):
    """Получен текст контента — финал"""
    content_text = message.text
    if content_text == "-":
        content_text = None
    
    # Получаем все данные
    data = await state.get_data()
    
    # TODO: Сохранение в БД
    # from bot.services.db import create_content_item
    # create_content_item(...)
    
    summary = (
        "✅ **Контент добавлен!**\n\n"
        f"📁 Категория: {data.get('content_type')}\n"
        f"📝 Название: {data.get('title')}\n"
        f"📄 Описание: {data.get('description')[:50]}...\n"
        f"🏷️ Стресс: {data.get('stress_type')}\n"
    )
    
    await message.reply(summary, parse_mode="Markdown")
    await state.clear()


# ============================================
# Удаление контента
# ============================================

@router.callback_query(F.data == "admin_delete_content")
async def on_admin_delete_content(callback: types.CallbackQuery, state: FSMContext):
    """Начать удаление контента"""
    await callback.message.edit_text(
        "🗑️ **Удаление контента**\n\nВведите **ID** контента для удаления:",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminDeleteContent.waiting_for_content_id)


@router.message(AdminDeleteContent.waiting_for_content_id)
async def on_delete_content_id(message: types.Message, state: FSMContext):
    """Получен ID для удаления"""
    try:
        content_id = int(message.text)
    except ValueError:
        await message.reply("❌ Введите корректный ID (число):", reply_markup=get_cancel_keyboard())
        return
    
    await state.update_data(content_id=content_id)
    
    # TODO: Проверка существования контента в БД
    
    await message.reply(
        f"⚠️ Вы уверены, что хотите удалить контент с ID **{content_id}**?\n\nЭто действие нельзя отменить.",
        parse_mode="Markdown",
        reply_markup=get_confirm_keyboard()
    )


@router.callback_query(F.data == "confirm_yes")
async def on_confirm_delete(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение удаления"""
    data = await state.get_data()
    content_id = data.get("content_id")
    
    # TODO: Удаление из БД
    # delete_content(content_id)
    
    await callback.message.edit_text(f"✅ Контент с ID {content_id} удалён!")
    await state.clear()


@router.callback_query(F.data == "confirm_no")
async def on_confirm_cancel(callback: types.CallbackQuery, state: FSMContext):
    """Отмена удаления"""
    await state.clear()
    await callback.message.edit_text("❌ Удаление отменено")
