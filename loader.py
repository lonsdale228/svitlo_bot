import logging
import os
import redis.asyncio as redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

if os.name == 'nt':
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8", decode_responses=True)
else:
    r = redis.from_url("redis://redis:6379", encoding="utf8", decode_responses=True)

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)