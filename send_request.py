import aiohttp
from config import url_on, url_off


async def send_on_request():
    async with aiohttp.ClientSession() as session:
        async with session.post(url_on) as response:
            ...


async def send_off_request():
    async with aiohttp.ClientSession() as session:
        async with session.post(url_off) as response:
            ...