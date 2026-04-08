import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Создаём директорию для логов, если её нет
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Настройка форматирования
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "psycho_bot", level: int = logging.INFO):
    """Настраивает и возвращает логгер с выводом в консоль и файл"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Если уже есть обработчики, не добавляем заново
    if logger.handlers:
        return logger

    # Форматтер
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Обработчик для файла (ротация: 5 файлов по 5 МБ)
    file_handler = RotatingFileHandler(
        LOG_DIR / "bot.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Создаём логгеры для разных модулей
bot_logger = setup_logger("bot")
handlers_logger = setup_logger("handlers")
nlp_logger = setup_logger("nlp")
recommender_logger = setup_logger("recommender")
db_logger = setup_logger("db")
