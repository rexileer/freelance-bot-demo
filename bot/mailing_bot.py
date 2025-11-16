import time
from aiogram import Bot, Dispatcher
import os
from aiogram.enums import ParseMode
from datetime import datetime
from django.db.models import Q
from bot.components.connectors import postgres_connector
from django.utils import timezone
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import FSInputFile



async def start():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    while True:
        # for payment in await postgres_connector.get_payments():
        #
        async for bid in await postgres_connector.get_mailings():
            await postgres_connector.update_complete_status_bid(bid)
            users = await postgres_connector.get_users_by_bid_matters(bid)
            bid_files = [file async for file in await postgres_connector.get_files_by_bid(bid)]
            if len(bid_files) > 10: bid_files = bid_files[:10]
            builder = MediaGroupBuilder()
            for i, file in enumerate(bid_files):
                print(file.path)
                media_file = file.tg_file_id if file.tg_file_id else FSInputFile("bot/media/" + str(file.path))
                if file.file_type == "photo":
                    builder.add_photo(media_file, caption=bid.text if i == 0 else None)
                if file.file_type == "video":
                    builder.add_video(media_file, caption=bid.text if i == 0 else None)
                if file.file_type == "document":
                    builder.add_document(media_file, caption=bid.text if i == 0 else None)
            async for user_id in users:
                user = await postgres_connector.get_user_by_id(user_id)
                if not user.search_switch: continue
                if bid_files:
                    try:
                        await bot.send_media_group(chat_id=user.id, media=builder.build())
                    except Exception as ex:
                        print(f"ERROR: {ex}")
                else:
                    try:
                        await bot.send_message(chat_id=user.id, text=bid.text)
                    except Exception as ex:
                        print(f"ERROR: {ex}")
        time.sleep(2)

