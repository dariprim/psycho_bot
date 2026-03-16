# ============================================
# TG Bot "Твой психолог" 🧠
# Multi-stage Dockerfile (production-ready)
# ============================================

# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Системные зависимости для компиляции Python-пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем только requirements для кэширования слоёв
COPY requirements.txt .

# Установка зависимостей в отдельную директорию
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.12-slim AS runtime

WORKDIR /app

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Создаём непривилегированного пользователя для безопасности
RUN useradd --create-home --shell /bin/bash botuser

# Системные зависимости для runtime (только libpq для asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && chown -R botuser:botuser /app

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /home/botuser/.local

# Копируем исходный код
COPY --chown=botuser:botuser bot/ ./bot/
COPY --chown=botuser:botuser .env.example ./.env.example

# PATH для доступа к установленным пакетам
ENV PATH=/home/botuser/.local/bin:$PATH

# Переключаемся на непривилегированного пользователя
USER botuser

# Healthcheck для проверки работоспособности
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import bot.config; print('OK')" || exit 1

# Запуск бота
CMD ["python", "-m", "bot.main"]
