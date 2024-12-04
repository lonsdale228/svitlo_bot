import asyncio

import aiohttp
from config import url_on, url_off
from loader import logger

SLEEP_TIME = 60

async def send_on_request():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url_on) as response:
                if response.status != 200:
                    await asyncio.sleep(SLEEP_TIME)
                    await send_on_request()
    except Exception as e:
        logger.error(e)

async def send_off_request():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url_off) as response:
                if response.status != 200:
                    await asyncio.sleep(SLEEP_TIME)
                    await send_off_request()
    except Exception as e:
        logger.error(e)