import aiohttp
from config import url_on, url_off


async def send_on_request():
    async with aiohttp.ClientSession() as session:
        async with session.post(url_on) as response:
            if response.status == 200:
                data = await response.json()
                print("Response:", data)
            else:
                print(f"Request failed with status {response.status}")


async def send_off_request():
    async with aiohttp.ClientSession() as session:
        async with session.post(url_off) as response:
            if response.status == 200:
                data = await response.json()  # Parse JSON response
                print("Response:", data)
            else:
                print(f"Request failed with status {response.status}")