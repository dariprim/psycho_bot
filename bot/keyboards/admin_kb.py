from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Главное меню админ-панели"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Добавить контент", callback_data="admin_add_content"),
            ],
            [
                InlineKeyboardButton(text="✏️ Редактировать", callback_data="admin_edit_content"),
                InlineKeyboardButton(text="🗑️ Удалить", callback_data="admin_delete_content"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
                InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            ],
        ]
    )
    return keyboard


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура отмены"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")],
        ]
    )
    return keyboard


def get_content_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа контента"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Книги", callback_data="content_type_book"),
                InlineKeyboardButton(text="🎮 Игры", callback_data="content_type_game"),
            ],
            [
                InlineKeyboardButton(text="🧘 Техники", callback_data="content_type_technique"),
                InlineKeyboardButton(text="💪 Упражнения", callback_data="content_type_exercise"),
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")],
        ]
    )
    return keyboard


def get_stress_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа стресса"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😰 Тревога", callback_data="stress_anxiety"),
                InlineKeyboardButton(text="😢 Грусть", callback_data="stress_sadness"),
            ],
            [
                InlineKeyboardButton(text="😤 Стресс", callback_data="stress_stress"),
                InlineKeyboardButton(text="😡 Гнев", callback_data="stress_anger"),
            ],
            [
                InlineKeyboardButton(text="😴 Усталость", callback_data="stress_fatigue"),
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")],
        ]
    )
    return keyboard


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение действия"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no"),
            ],
        ]
    )
    return keyboard


def get_pagination_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Пагинация для списков"""
    buttons = []
    
    row = []
    if page > 1:
        row.append(InlineKeyboardButton(text="◀️", callback_data=f"page_{page - 1}"))
    
    for p in range(max(1, page - 2), min(total_pages + 1, page + 3)):
        row.append(InlineKeyboardButton(text=str(p), callback_data=f"page_{p}"))
    
    if page < total_pages:
        row.append(InlineKeyboardButton(text="▶️", callback_data=f"page_{page + 1}"))
    
    buttons.append(row)
    buttons.append([InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
