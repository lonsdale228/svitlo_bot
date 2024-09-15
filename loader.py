import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from handlers.admin import router

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML', link_preview_is_disabled=True))
dp = Dispatcher()
dp.include_router(router)
TIMEZONE = 'Europe/Kyiv'

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
