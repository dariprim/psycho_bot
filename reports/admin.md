#  Отчёт: Админ-команды

**Дата:** 16 марта 2026 г.  


---

## Что было сделано

### 1. **Настройка конфигурации** (`bot/config.py`)

Добавлена переменная для списка админов:

```python
# Admins (список Telegram ID через запятую)
ADMINS_RAW = os.getenv("ADMINS", "")
ADMINS = [int(x.strip()) for x in ADMINS_RAW.split(",") if x.strip().isdigit()]
```

**Пример в `.env`:**
```
ADMINS=123456789,987654321
```

---

### 2. **Клавиатуры для админ-панели** (`bot/keyboards/admin_kb.py`)

Создан новый модуль с inline-клавиатурами:

| Функция | Описание |
|---------|----------|
| `get_admin_keyboard()` | Главное меню админ-панели |
| `get_cancel_keyboard()` | Кнопка "❌ Отмена" |
| `get_content_type_keyboard()` | Выбор категории (📚 Книги, 🎮 Игры, ...) |
| `get_stress_type_keyboard()` | Выбор типа стресса (😰 Тревога, 😢 Грусть, ...) |
| `get_confirm_keyboard()` | Подтверждение (✅ Да / ❌ Нет) |
| `get_pagination_keyboard()` | Пагинация для списков |

**Пример главного меню:**
```
 Админ-панель

[➕ Добавить контент]
[✏️ Редактировать] [🗑️ Удалить]
[📊 Статистика] [👥 Пользователи]
```

---

### 3. **Обработчики команд** (`bot/handlers/admin.py`)

#### **Команда `/admin` — главное меню**

```python
@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.reply("❌ Доступ запрещён.")
        return
    
    await message.reply(
        "🛠️ **Админ-панель**\n\nВыберите действие:",
        reply_markup=get_admin_keyboard()
    )
```

---

#### **Команда `/add_content` — добавление контента (FSM)**

**Диалог добавления:**
```
1. Бот: Выберите категорию:
   [📚 Книги] [🎮 Игры] [🧘 Техники] [💪 Упражнения]

2. Бот: Введите название:
   → Админ: "Как перестать беспокоиться"

3. Бот: Введите описание:
   → Админ: "Классика по преодолению тревоги"

4. Бот: Введите метаданные (JSON) или `-`:
   → Админ: {"author": "Дейл Карнеги"}

5. Бот: Выберите тип стресса:
   [😰 Тревога] [😢 Грусть] [😤 Стресс] [😡 Гнев] [😴 Усталость]

6. Бот: Введите текст контента или `-`:
   → Админ: "1. Вдохните на 4 счёта..."

✅ Контент добавлен!
```

**FSM состояния:**
```python
class AdminAddContent(StatesGroup):
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_metadata = State()
    waiting_for_stress_type = State()
    waiting_for_content_text = State()
```

---

#### **Команда `/stats` — статистика бота**

```python
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    stats_text = (
        "📊 **Статистика бота**\n\n"
        "👥 Пользователи: 0 (пока нет данных)\n"
        "💬 Сообщений обработано: 0\n"
        "📚 Контент в базе: 0\n"
        "🕒 Аптайм: 0 дней\n\n"
        "_Статистика будет доступна после подключения БД_"
    )
    await message.reply(stats_text, parse_mode="Markdown")
```

---

#### **Удаление контента (callback)**

```
1. Админ нажимает "🗑️ Удалить"
2. Бот: Введите ID контента:
   → Админ: 42
3. Бот: ⚠️ Вы уверены?
   [✅ Да] [❌ Нет]
4. Бот: ✅ Контент удалён!
```

---

### 4. **Регистрация в `bot/main.py`**

```python
from bot.handlers import common, admin

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_router(common.router)
    dp.include_router(admin.router)
    
    await set_bot_commands(bot)
    await dp.start_polling(bot)
```

**Админ-команды в меню бота:**
```python
if ADMINS:
    commands.extend([
        BotCommand(command="admin", description="Админ-панель"),
        BotCommand(command="add_content", description="Добавить контент"),
        BotCommand(command="stats", description="Статистика бота"),
    ])
```

---

##  Изменённые файлы

| Файл | Изменения |
|------|-----------|
| `bot/config.py` | +3 строки (ADMINS) |
| `bot/handlers/admin.py` | +295 строк (новый файл) |
| `bot/handlers/__init__.py` | +3 строки |
| `bot/keyboards/__init__.py` | +1 строка (новый файл) |
| `bot/keyboards/admin_kb.py` | +88 строк (новый файл) |
| `bot/main.py` | +10 строк (обновление) |
| `.env.example` | +3 строки (ADMINS) |

**Всего:** ~430 строк кода

---

##  Проверка прав админа

```python
async def is_admin(user_id: int) -> bool:
    """Проверка: является ли пользователь админом"""
    return user_id in ADMINS


async def admin_only(message: types.Message) -> bool:
    """Фильтр только для админов"""
    if not await is_admin(message.from_user.id):
        await message.reply("❌ Доступ запрещён.")
        return False
    return True
```

**Использование:**
```python
@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not await admin_only(message):
        return  # Доступ запрещён
    # Показываем админ-панель
```

---

##  Доступные команды

| Команда | Описание | Доступ |
|---------|----------|--------|
| `/admin` | Админ-панель (главное меню) | Только админы |
| `/add_content` | Добавить контент (диалог) | Только админы |
| `/stats` | Статистика бота | Только админы |
| `/start`, `/help`, `/info` | Обычные команды | Все пользователи |

---

##  Как использовать

### **1. Настройка .env**

```bash
# Узнать свой Telegram ID можно у бота @userinfobot
ADMINS=123456789
```

### **2. Запуск бота**

```bash
python -m bot.main
```

### **3. Проверка команд**

```
/admin → открыть админ-панель
/add_content → начать добавление контента
/stats → посмотреть статистику
```

---

##  Структура админ-панели

```
🛠️ Админ-панель
│
├── ➕ Добавить контент
│   ├── Выбор категории
│   ├── Название
│   ├── Описание
│   ├── Метаданные (JSON)
│   ├── Тип стресса
│   └── Текст контента
│
├── ✏️ Редактировать
│   └── (в разработке)
│
├── 🗑️ Удалить
│   ├── Ввод ID
│   └── Подтверждение
│
├── 📊 Статистика
│   └── (заглушка)
│
└── 👥 Пользователи
    └── (в разработке)
```

---

##  TODO (не реализовано)

1. **Сохранение в БД** — в `/add_content` нужна интеграция с `bot/services/db.py`
2. **Редактирование контента** — команда `/edit_content`
3. **Список пользователей** — команда `/users` с пагинацией
4. **Рассылка** — команда `/broadcast` для уведомлений
5. **Реальная статистика** — запросы к БД для `/stats`

---