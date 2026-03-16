import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN, ADMINS
from bot.handlers import common, admin
from aiogram.types import BotCommand

logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать новый диалог"),
        BotCommand(command="help", description="Справка о боте"),
        BotCommand(command="info", description="Службы помощи"),
    ]
    
    # Админ-команды (видны только админам)
    if ADMINS:
        commands.extend([
            BotCommand(command="admin", description="Админ-панель"),
            BotCommand(command="add_content", description="Добавить контент"),
            BotCommand(command="stats", description="Статистика бота"),
        ])
    
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_router(common.router)
    dp.include_router(admin.router)
    
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())