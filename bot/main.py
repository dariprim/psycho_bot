import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN, ADMINS
from bot.handlers import common, admin
from aiogram.types import BotCommand
from bot.utils.logger import bot_logger

logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать новый диалог"),
        BotCommand(command="help", description="Справка о боте"),
        BotCommand(command="info", description="Службы помощи"),
    ]

    # Админ-команды (видны только админам)
    if ADMINS:
        commands.extend(
            [
                BotCommand(command="admin", description="Админ-панель"),
                BotCommand(command="add_content", description="Добавить контент"),
                BotCommand(command="stats", description="Статистика бота"),
            ]
        )

    await bot.set_my_commands(commands)


async def main():
    bot_logger.info("Starting bot...")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)

    await set_bot_commands(bot)
    bot_logger.info("Bot started, polling...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        bot_logger.error(f"Polling error: {e}", exc_info=True)
    finally:
        bot_logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
