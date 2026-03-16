# 📊 Отчёт: Изменения в базе данных

**Дата:** 16 марта 2026 г.  


---

##  Что было сделано

### 1. **Обновлены модели данных** (`bot/models/db_models.py`)

**Старые таблицы:**
- `books` — книги
- `games` — игры

**Новые таблицы:**
- `users` — пользователи бота
- `categories` — категории контента
- `content_items` — контент (универсальная таблица)
- `feedback` — обратная связь от пользователей

---

##  Описание таблиц

### **1. users** — Пользователи

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Primary Key |
| `telegram_id` | BigInteger | Уникальный ID Telegram (индекс) |
| `username` | String(100) | Имя пользователя |
| `first_name` | String(100) | Имя |
| `last_name` | String(100) | Фамилия |
| `preferences` | JSON | Настройки и предпочтения |
| `mood_history` | JSON | История настроений (последние 100 записей) |
| `total_interactions` | Integer | Счётчик взаимодействий |
| `last_interaction` | DateTime | Дата последнего взаимодействия |
| `created_at` | DateTime | Дата регистрации |
| `updated_at` | DateTime | Дата обновления |

**Пример JSON в `preferences`:**
```json
{
  "preferred_content_type": "technique",
  "notification_enabled": true,
  "language": "ru"
}
```

**Пример JSON в `mood_history`:**
```json
[
  {
    "mood": "anxious",
    "stress_type": "anxiety",
    "timestamp": "2026-03-16T14:30:00Z"
  }
]
```

---

### **2. categories** — Категории контента

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Primary Key |
| `name` | String(100) | Название (уникальное) |
| `description` | Text | Описание |
| `content_type` | String(50) | Тип: book, game, technique, exercise |
| `stress_types` | JSON | Для каких состояний рекомендуется |
| `is_active` | Integer | Статус (1=активна, 0=скрыта) |
| `sort_order` | Integer | Порядок сортировки |

**Пример категорий:**
```
1. Книги (book)
2. Игры (game)
3. Техники (technique)
4. Упражнения (exercise)
```

---

### **3. content_items** — Контент

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Primary Key |
| `category_id` | Integer | Foreign Key → categories |
| `title` | String(200) | Название |
| `description` | Text | Описание |
| `metadata` | JSON | Дополнительные данные |
| `stress_type` | String(50) | Для какого состояния |
| `content_text` | Text | Текст техники/упражнения |
| `external_url` | String(500) | Ссылка на внешний ресурс |
| `usage_count` | Integer | Счётчик использований |
| `positive_feedback` | Integer | Счётчик + |
| `negative_feedback` | Integer | Счётчик - |
| `is_active` | Integer | Статус |
| `created_at` | DateTime | Дата создания |
| `updated_at` | DateTime | Дата обновления |

**Пример JSON в `metadata`:**
```json
// Для книги
{"author": "Дейл Карнеги", "year": 1948}

// Для игры
{"platform": "PC, Switch", "genre": "Simulation"}
```

---

### **4. feedback** — Обратная связь

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Primary Key |
| `user_id` | Integer | Foreign Key → users |
| `content_item_id` | Integer | Foreign Key → content_items |
| `is_positive` | Integer | 1=понравилось, 0=не понравилось |
| `comment` | Text | Комментарий (опционально) |
| `created_at` | DateTime | Дата отзыва |

---

##  Связи между таблицами

```
users (1) ────── (M) feedback
                        │
                        │
categories (1) ── (M) content_items (1) ────── (M) feedback
```

**Связи:**
- `User` → `Feedback`: один ко многим (cascade delete)
- `Category` → `ContentItem`: один ко многим (cascade delete)
- `ContentItem` → `Feedback`: один ко многим (cascade delete)

---

##  Изменённые файлы

| Файл | Изменения |
|------|-----------|
| `bot/models/db_models.py` | +129 строк (4 новые модели + enum StressType) |
| `bot/services/db.py` | +220 строк (функции для работы с БД) |
| `init_db.py` | +148 строк (новые тестовые данные) |

---

##  Новые функции в `bot/services/db.py`

### **Пользователи**
```python
get_or_create_user(telegram_id, username, first_name, last_name)
update_user_interaction(user_id)
update_user_mood(user_id, mood, stress_type)
```

### **Категории**
```python
get_all_categories()
get_category_by_id(category_id)
```

### **Контент**
```python
get_content_items(category_id, stress_type, limit)
get_random_content(stress_type, content_type)
get_content_by_id(content_id)
increment_usage_count(content_id)
```

### **Обратная связь**
```python
add_feedback(user_id, content_item_id, is_positive, comment)
```

### **Утилиты**
```python
get_all_stress_types()  # ['anxiety', 'sadness', 'stress', 'anger', 'fatigue']
drop_all_tables()       # Для тестов
```

---

##  Тестовые данные

**Категории (4):**
1. Книги (3 элемента)
2. Игры (3 элемента)
3. Техники (3 элемента)
4. Упражнения (2 элемента)

**Всего контента:** 11 элементов

**Типы стресса (StressType enum):**
- `anxiety` — Тревога
- `sadness` — Грусть/депрессия
- `stress` — Стресс
- `anger` — Гнев
- `fatigue` — Усталость

---

##  Команды для проверки

```bash
# Инициализация БД (создание таблиц + тестовые данные)
python init_db.py

# Проверка через PostgreSQL
docker-compose exec postgres psql -U botuser -d psychobot -c "SELECT * FROM users;"
docker-compose exec postgres psql -U botuser -d psychobot -c "SELECT * FROM categories;"
docker-compose exec postgres psql -U botuser -d psychobot -c "SELECT * FROM content_items;"
```
