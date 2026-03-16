#  Отчёт по Docker-настройке

**Дата:** 16 марта 2026 г.  


### 1. **Dockerfile** (multi-stage, production-ready)

**Путь:** `/Dockerfile`

**Особенности:**
- ✅ **Multi-stage сборка** — уменьшает размер образа (нет компиляторов в runtime)
- ✅ **Python 3.12-slim** — минимальный базовый образ
- ✅ **Непривилегированный пользователь** (`botuser`) — безопасность
- ✅ **HEALTHCHECK** — мониторинг работоспособности
- ✅ **Оптимизация кэширования** — слои пересобираются только при изменении зависимостей

**Структура:**
```
Stage 1: Builder
  ├─ Установка build-essential, libpq-dev
  ├─ Установка Python-зависимостей в /root/.local
  └─ Кэширование слоя с requirements.txt

Stage 2: Runtime
  ├─ Минимальный образ (python:3.12-slim)
  ├─ Копирование пакетов из builder
  ├─ Настройка пользователя botuser
  ├─ HEALTHCHECK (проверка каждые 30 сек)
  └─ Запуск бота
```

---

### 2. **docker-compose.yml** (оркестрация сервисов)

**Путь:** `/docker-compose.yml`

**Сервисы:**

| Сервис | Образ | Порты | Назначение |
|--------|-------|-------|------------|
| `bot` | build (Dockerfile) | — | Основной бот (Aiogram) |
| `postgres` | postgres:16-alpine | 5432 | База данных |
| `redis` | redis:7-alpine | 6379 | Кэш, сессии, очереди |

**Volumes (постоянное хранение):**
- `postgres_data` — данные PostgreSQL
- `redis_data` — данные Redis (AOF персистентность)
- `model_volume` — ML-модели (монтируются в бот)

**Networks:**
- `bot_network` (bridge) — изолированная сеть для сервисов

**Healthchecks:**
- ✅ bot: проверка импорта конфига
- ✅ postgres: `pg_isready`
- ✅ redis: `redis-cli ping`

---

### 3. **.dockerignore**

**Путь:** `/.dockerignore`

**Исключает:**
-  `.env` — секреты не попадают в образ
-  `models/`, `*.gguf` — модели весят много, монтируются volume
-  `tests/`, `pytest_cache/` — тесты не нужны в production
-  `__pycache__/`, `*.pyc` — кэш байт-кода
-  `.git/`, `.idea/`, `.vscode/` — служебные файлы

---

### 4. **Обновлённые файлы**

| Файл | Изменения |
|------|-----------|
| `.env.example` | Добавлен `REDIS_URL`, обновлены комментарии |
| `bot/config.py` | Добавлена переменная `REDIS_URL` |
| `requirements.txt` | Добавлен `redis>=5.0.0` |

---

## Ключевые команды

### **Первый запуск**

```bash
# 1. Создать .env из примера
cp .env.example .env

# 2. Отредактировать .env (вставить BOT_TOKEN)
#    BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# 3. Собрать образы
docker-compose build

# 4. Запустить все сервисы (фоновый режим)
docker-compose up -d

# 5. Проверить статус
docker-compose ps
```

---

### **Мониторинг**

```bash
# Логи всех сервисов
docker-compose logs

# Логи конкретного сервиса (например, бота)
docker-compose logs -f bot

# Статус сервисов (включая healthcheck)
docker-compose ps

# Проверка healthcheck контейнера
docker inspect --format='{{.State.Health.Status}}' psycho_bot

# Использование ресурсов
docker stats
```

---

### **Остановка и перезапуск**

```bash
# Остановка всех сервисов
docker-compose down

# Остановка + удаление volumes ( данные БД удалятся!)
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart bot

# Пересборка и перезапуск
docker-compose up -d --build
```

---

### **Работа с контейнерами**

```bash
# Войти в контейнер с ботом (для отладки)
docker-compose exec bot bash

# Войти в контейнер с PostgreSQL
docker-compose exec postgres psql -U botuser -d psychobot

# Войти в контейнер с Redis
docker-compose exec redis redis-cli

# Просмотр переменных окружения в контейнере
docker-compose exec bot env
```

---

### **Сборка и кэширование**

```bash
# Пересборка без кэша (полная сборка)
docker-compose build --no-cache

# Сборка только одного сервиса
docker-compose build bot

# Очистка неиспользуемых образов
docker image prune -a

# Очистка всех остановленных контейнеров
docker container prune
```

---

##  Структура файлов

```
psycho_bot-dariprim/
├── Dockerfile              # Multi-stage сборка
├── docker-compose.yml      # Оркестрация 3 сервисов
├── .dockerignore           # Исключения для сборки
├── .env.example            # Шаблон переменных окружения
├── .env                    # Реальные настройки (не в git!)
├── requirements.txt        # Python-зависимости
├── bot/
│   ├── main.py             # Точка входа
│   └── config.py           # Конфигурация (с REDIS_URL)
├── models/                 # ML-модели (монтируются volume)
└── reports/
    └── docker.md           # Этот отчёт
```
