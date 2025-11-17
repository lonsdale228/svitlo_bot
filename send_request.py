import asyncio
import os

import aiohttp
from loader import logger

SLEEP_TIME = 60

url_on = os.getenv("url_on")
url_off = os.getenv("url_off")


async def send_on_request():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url_on) as response:
                logger.info("Send ON Request")
                if response.status != 200:
                    await asyncio.sleep(SLEEP_TIME)
                    await send_on_request()
    except Exception as e:
        logger.error(e)


async def send_off_request():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url_off) as response:
                logger.info("Send OFF Request")
                if response.status != 200:
                    await asyncio.sleep(SLEEP_TIME)
                    await send_off_request()
    except Exception as e:
        logger.error(e)

# async def send_request(is_on: bool):
#     status_code = None
#     while status_code!=200:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url_off) as response:
#                 status_code = response.status
#                 await asyncio.sleep(SLEEP_TIME)
#                 await send_off_request()
