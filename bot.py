import asyncio
import json

from aiogram import Bot
from redis import Redis

from loader import bot, dp, r, logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp


async def check_electricity_change():
    current_status = await r.get('status').decode()
    prev_status = await r.get('prev_status').decode()

    if current_status != prev_status:
        await r.set('status', current_status)
        await send_notification()
    else:
        ...


async def dtek_checker(redis: Redis):
    d = {}
    url = "https://www.dtek-oem.com.ua/ua/ajax"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-UA,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk-UA;q=0.6,uk;q=0.5,ru-RU;q=0.4",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "Domain=dtek-oem.com.ua; _language=4feef5ffdc846bbf9c35c97292b7b3e6c48117a536a6462b530e0984a39d6bd4a%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_language%22%3Bi%3A1%3Bs%3A2%3A%22uk%22%3B%7D; visid_incap_2398477=nlmTkLtQTPK+jG2ySsAHo/OfhmYAAAAAQUIPAAAAAAC0bcqapaAK61SKObnQjm0v; _hjSessionUser_2709929=eyJpZCI6ImEyMDNmZDQ1LTcxNWEtNTNkZS04MmZlLWQwM2JjZGFhNmM2MSIsImNyZWF0ZWQiOjE3MjA0NjUyMjgwNDYsImV4aXN0aW5nIjp0cnVlfQ==; dtek-oem=9glldki82734g88nud4s7vmoe7; _csrf-dtek-oem=3bdc2d9f8555486fbd98926f09a462c7cb44b526e0356799a8cc78b2316a89fca%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-dtek-oem%22%3Bi%3A1%3Bs%3A32%3A%22Xcl86gyo6ghCQ7hidG6oJomJliiWvScf%22%3B%7D; incap_ses_688_2398477=3NAoY5wrJiFZSzZydESMCV4eomYAAAAApE8Wf34KGJuzjN7n54O/pw==; _ga_B5BT53GY2T=GS1.1.1721900639.8.0.1721900639.60.0.0; _ga=GA1.3.1601181530.1720098805; _gid=GA1.3.1330908646.1721900640; _gat_gtag_UA_141782039_1=1; incap_wrt_377=ah6iZgAAAACXPPY8GQAI+QIQ87/3iCsYlr+ItQYgAijdvIi1BjAB2uy2xHACsDVg2Kg6OsArmQ==",
        "Origin": "https://www.dtek-oem.com.ua",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Referer": "https://www.dtek-oem.com.ua/ua/shutdowns",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "X-Csrf-Token": "5WKzViDLVSWZEd-q-OvB-qQ6-AQodB94nhPBRbP0hYm9Ad9uFqwsSq92t-mp3KmTwH3Oa2IbcjLyeqgSxafm7w==",
        "X-Requested-With": "XMLHttpRequest"
    }

    payload = {
        "method": "getHomeNum",
        "data[0][name]": "city",
        "data[0][value]": "с. Лиманка",
        "data[1][name]": "street",
        "data[1][value]": "вул. Затишна"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            response_text = await response.text()
            js = json.loads(response_text)
            await redis.set("dtek_update_timestamp", js["updateTimestamp"])


async def send_notification():
    ...

async def msg_editor(b: Bot):
    dtek_last_update = await r.get('dtek_update_timestamp')
    msg = await b.edit_message_text(dtek_last_update, chat_id=317465871, message_id=5)

async def main():
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(check_electricity_change, 'interval', seconds=3)
    scheduler.add_job(dtek_checker, 'interval', seconds=10, jitter=1, args=(r,))
    scheduler.add_job(msg_editor, 'interval', seconds=10, args=(bot,))
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
