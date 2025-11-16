from telethon import TelegramClient, utils
from telethon import events
from .components import postgres_connector
from asgiref.sync import sync_to_async
import os
from telethon import functions
import re
from telethon.errors import (
    FloodWaitError,
)
import asyncio
from pprint import pprint

client = None

async def match_keywords(message_text):
    subject_matters = []
    async for matter in await postgres_connector.get_subject_matters():
        for keyword in matter.keywords.split(","):
            if keyword.strip() in message_text:
                subject_matters.append(matter)
                break
    return subject_matters

async def get_user_url_by_id(user_id):
    try:
        user = await client(functions.users.GetFullUserRequest(user_id))
        user = user.to_dict()["users"][0]
        if user["username"]:
            user_url = 'https://t.me/' + user['username']
            return user_url
    except FloodWaitError as err:
        print(f"Flood wait error received. Sleep {err.seconds} seconds")
        await asyncio.sleep(err.seconds)
        return await get_user_url_by_id(user_id)


def get_author_contacts_exist(message_text):
    phone_exist = bool(re.findall(r"\+?(7|8)[ -]?(\(?\d{3}\)?[ -]?)?\d{3}[ -]?\d{2}[ -]?\d{2}", message_text))
    tg_link_exist = bool(re.findall(r"(?:https://t\.me/[A-Za-z0-9_]+|@[A-Za-z0-9_]+)", message_text))
    return phone_exist or tg_link_exist


async def _ensure_client():
    global client
    if client is None:
        api_id = os.getenv("TG_PARSER_API_ID")
        api_hash = os.getenv("TG_PARSER_API_HASH")
        if not api_id or not api_hash:
            return None
        client = TelegramClient("tg_parser_session_parser", api_id, api_hash)
    return client

async def new_message_handler(event):
    message = event.message.to_dict()
    chat_id = None
    channel_id = None
    author_id = None
    author = None
    if message["peer_id"]["_"] == "PeerChannel":
        channel_id = message["peer_id"]["channel_id"]
    elif message["peer_id"]["_"] == "PeerChat":
        chat_id = message["peer_id"]["chat_id"]
        author_id = int(message["from_id"]["user_id"])
    if not await postgres_connector.channel_is_exist(tg_id=channel_id if channel_id else chat_id):
        return
    if re.findall("(?:https://t.me/[^ ]+?bot *\\n*|@[^ ]+?bot *\\n*)", message["message"]):
        return
    print("channel_id ", channel_id)
    print(message["message"])
    print("")
    author_contacts_exist = get_author_contacts_exist(message["message"])
    if not author_contacts_exist and author_id:
        author = await get_user_url_by_id(author_id)

    if author or author_contacts_exist:
        matters = await match_keywords(message["message"])
        if matters:
            text = f"""📍 {', '.join([matter.name for matter in matters])}\n\n🔘 {message["message"]}"""
            text = text if not author else f'{text}\n\n📩 Контакты - {author}'
            await postgres_connector.add_bid(matters, author, channel_id if channel_id else chat_id, text)


async def run():
    api_id = os.getenv("TG_PARSER_API_ID")
    api_hash = os.getenv("TG_PARSER_API_HASH")
    if not api_id or not api_hash:
        print("Parser stub: TG_PARSER_API_ID/TG_PARSER_API_HASH not set. Parser is disabled in demo mode.")
        # Sleep forever with periodic heartbeat to keep container healthy if needed
        while True:
            await asyncio.sleep(3600)
    print("Start parser")
    cli = await _ensure_client()
    if cli is None:
        return
    cli.add_event_handler(new_message_handler, events.NewMessage())
    await cli.start(bot_token=os.getenv("BOT_TOKEN"))
    await cli.run_until_disconnected()
