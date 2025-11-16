import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
import os
from bot.components.handlers import (main_menu, subject_matters, personal_account, referral_system, useful_materials)
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger


async def run():
    def register_handlers(dp: Dispatcher):
        main_menu.register_handlers(dp)
        subject_matters.register_handlers(dp)
        personal_account.register_handlers(dp)
        referral_system.register_handlers(dp)
        useful_materials.register_handlers(dp)

    async def set_commands(bot: Bot):
        commands = [
            BotCommand(
                command="start",
                description="Запустить бота",
            ),
            BotCommand(
                command="help",
                description="Справка",
            )
        ]
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

    dp = Dispatcher()
    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(bot_token, disable_web_page_preview=True)
    bot_info = await bot.get_me()
    logger.info(f'Starting bot {bot_info.username}')
    await set_commands(bot)
    await bot.send_message(text="/start", chat_id=os.getenv("ADMIN_ID"))
    register_handlers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(run())
