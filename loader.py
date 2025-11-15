import logging
import os

import nest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from pyrogram import Client
import tgcrypto
from handlers.admin import router
nest_asyncio.apply()



load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True),
)
dp = Dispatcher()
dp.include_router(router)
TIMEZONE = "Europe/Kyiv"

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

dtek_timetable_bot = Client(
    "dtek_timetable_bot", api_id=API_ID, api_hash=API_HASH, plugins=dict(root="plugins")
)


logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
