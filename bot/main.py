import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import common
from aiogram.types import BotCommand

logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать новый диалог"),
        BotCommand(command="info", description="Службы помощи"),
    ]
    await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)
    await set_bot_commands(bot) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())