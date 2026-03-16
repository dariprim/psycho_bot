import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://botuser:botpassword@localhost:5432/psychobot")

# Redis (кэш, сессии, очереди)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ML Models
MODEL_PATH = os.getenv("MODEL_PATH", "/models/YandexGPT-5-Lite-8B-instruct-Q4_K_M.gguf")
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "blanchefort/rubert-base-cased-sentiment")