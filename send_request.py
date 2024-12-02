import aiohttp
from config import url_on, url_off
from loader import logger


async def send_on_request():
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url_on)
    except Exception as e:
        logger.error(e)

async def send_off_request():
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url_off)
    except Exception as e:
        logger.error(e)