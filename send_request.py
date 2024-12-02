import aiohttp
from config import url_on, url_off
from loader import logger


async def send_on_request():
    async with aiohttp.ClientSession() as session:
        async with session.post(url_on) as response:
            try:
                data = await response.text()
                print(data)
            except Exception as e:
                logger.error(e)


async def send_off_request():
    async with aiohttp.ClientSession() as session:
        async with session.post(url_off) as response:
            try:
                data = await response.text()
                print(data)
            except Exception as e:
                logger.error(e)