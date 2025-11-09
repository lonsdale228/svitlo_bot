import asyncio
import datetime
import json
import os

import pytz
from aiogram import Bot
from redis import Redis

from loader import bot, dp, logger, TIMEZONE
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

from models import Zone
from redis_loader import r
from send_request import send_on_request, send_off_request
from utils import time_format, get_next_zones, time_with_tz, zone_to_string
from timetables import zones
import handlers

MY_ID = os.getenv('CHANNEL_ID')
DTEK_UPDATE_INTERVAL = 90
MSG_UPDATE_INTERVAL = 10
REGION_NAME = "с. Лиманка"
STREET_NAME = "вул. Затишна"
HOUSE_NUM = "10"
DONATE_LINK = os.getenv('DONATE_LINK')


# REGION_NAME = "м. Одеса"
# STREET_NAME = "вул. Інглезі"
# HOUSE_NUM = "1"


def to_int_or_none(val):
    return None if val is None else int(val)


async def check_electricity_change(lock):
    pause = int(await r.get('pause'))

    if pause != 1:
        current_status = await r.get('status')
        prev_status = await r.get('prev_status')

        current_status = to_int_or_none(current_status)
        prev_status = to_int_or_none(prev_status)

        # at first start
        if (current_status is not None) and (prev_status is None):
            await r.set('prev_status', current_status)

        if current_status != prev_status:
            async with lock:
                await send_change_msg(current_status)
            await r.set('prev_status', current_status)
        else:
            ...
    else:
        logger.info("Paused...")


async def send_change_msg(is_on: int):
    msg_text = f""

    now = time_with_tz()
    now_strf = now.strftime("%H:%M:%S")

    off_time = datetime.datetime.fromtimestamp(float(await r.get("off_time")))
    on_time = datetime.datetime.fromtimestamp(float(await r.get("on_time")))

    tz_info_off_time = off_time.tzinfo
    tz_info_on_time = on_time.tzinfo

    prev_msg_id = int(await r.get("edit_msg_id"))

    send_request = int(await r.get("send_request"))

    if is_on == 1:
        if send_request == 1:
            asyncio.create_task(send_on_request())
        msg_text += "💡Світло з'явилося!"
        await r.set("on_time", str(now.timestamp()))

        prev_msg_text = (f"<i>Світла не було: \n"
                         f"з {off_time.strftime("%H:%M:%S")} по {now_strf} \n"
                         f"Протягом: \n"
                         f"{time_format((now.replace(tzinfo=tz_info_off_time) - off_time).total_seconds())}</i>")
        prev_msg_text += ("\n\n"
                          f"<a href='{DONATE_LINK}'>До чаю</a>")

    else:
        # send post
        if send_request == 1:
            asyncio.create_task(send_off_request())
        msg_text += "⚫️Світло зникло!"
        await r.set("off_time", str(now.timestamp()))
        prev_msg_text = (f"<i>Світло було: \n"
                         f"з {on_time.strftime("%H:%M:%S")} по {now_strf} \n"
                         f"Протягом: \n"
                         f"{time_format((now.replace(tzinfo=tz_info_on_time) - on_time).total_seconds())}</i>")
        prev_msg_text += ("\n\n"
                          f"<a href='{DONATE_LINK}'>До чаю</a>")


    msg = await bot.send_message(MY_ID, msg_text, disable_notification=False)

    await bot.edit_message_text(text=prev_msg_text, chat_id=MY_ID, message_id=prev_msg_id)

    await r.set("prev_msg_id", prev_msg_id)
    await r.set("edit_msg_id", msg.message_id)


async def dtek_checker(redis: Redis):
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
        "X-Csrf-Token": "2YjUYfDglXl6mBJzW0UmAhUNUf9pLI-2rEOBU-6rUUXuw602l47MPBiheiAJDFBKU3U0uxAZ2fyeCcsCrNg6Kg==",
        "X-Requested-With": "XMLHttpRequest"
    }

    url = "https://www.dtek-oem.com.ua/ua/ajax"
    REGION_NAME = "с. Лиманка"
    STREET_NAME = "вул. Затишна"
    HOUSE_NUM = "10"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-UA,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk-UA;q=0.6,uk;q=0.5,ru-RU;q=0.4",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "Domain=dtek-oem.com.ua; _language=4feef5ffdc846bbf9c35c97292b7b3e6c48117a536a6462b530e0984a39d6bd4a%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_language%22%3Bi%3A1%3Bs%3A2%3A%22uk%22%3B%7D; visid_incap_2398477=ghJ0YgB6R/KpZqwEZxd+EoTBuWcAAAAAQUIPAAAAAADnQgnSvBV37xZZSm1fpS2A; _hjSessionUser_2709929=eyJpZCI6ImEyMDNmZDQ1LTcxNWEtNTNkZS04MmZlLWQwM2JjZGFhNmM2MSIsImNyZWF0ZWQiOjE3MjA0NjUyMjgwNDYsImV4aXN0aW5nIjp0cnVlfQ==; dtek-oem=270l552t6ieairkj86vu0rvsbs; _csrf-dtek-oem=e8a957ff6d0501cd896ae0d5d4f71df37f4d2d3b83834278c677f85ef15485f5a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-dtek-oem%22%3Bi%3A1%3Bs%3A32%3A%22F6rC_JSWvCHY90MNFplfGz2RG87NH3bB%22%3B%7D; incap_ses_688_2398477=69b1dXNC8R3mpdgjDqAkDITBuWcAAAAAlLWhTrVrjoQMNEq5zfa/3A==; _ga_B5BT53GY2T=GS1.1.1740226949.1.0.1740226949.60.0.0; _ga=GA1.3.1034517031.1740226950; _gid=GA1.3.548904090.1740226950; _gat_gtag_UA_141782039_1=1; incap_wrt_377=kcG5ZwAAAAALawVxGQAI+QIQ7vmbnFAYvYXnvQYgAiiFg+e9BjABp6YztWQ5tmYh13BRxr9v5Q==",
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "X-Csrf-Token": "gJASGCjYpQvg7GGEDT4eIueld_RnbGIshdRB5sH4ZijGpmBbd5L2XJavKd00DlNsodUbkiAWUH7C7HaoicsEag==",
        "X-Requested-With": "XMLHttpRequest"
    }

    payload = {
        "method": "getHomeNum",
        "data[0][name]": "city",
        "data[0][value]": REGION_NAME,
        "data[1][name]": "street",
        "data[1][value]": STREET_NAME
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, data=payload) as response:
                response_text = await response.text()
                if "ROBOT" in response_text:
                    await asyncio.sleep(2)
                    await dtek_checker(redis)
                    return
                logger.debug(response_text)
                js = json.loads(response_text)
                await redis.set("dtek_update_timestamp", js["updateTimestamp"])
                await redis.set("sub_type", js['data'][HOUSE_NUM]['sub_type'])
                await redis.set("start_date", js['data'][HOUSE_NUM]['start_date'])
                await redis.set("end_date", js['data'][HOUSE_NUM]['end_date'])
                await redis.set("type", js['data'][HOUSE_NUM]['type'])
                await redis.set("sub_type_reason", js['data'][HOUSE_NUM]['sub_type_reason'][0])
    except Exception as e:
        logger.error(e)


async def send_notification(b: Bot, first_start=True):
    if first_start:
        msg = await b.send_message(MY_ID, 'Bot started!', disable_notification=True)
        await r.set('edit_msg_id', msg.message_id)


async def msg_editor(b: Bot, lock):
    global zones, DONATE_LINK

    async with lock:
        msg_to_edit = await r.get('edit_msg_id')
    dtek_last_update = await r.get('dtek_update_timestamp')
    status = await r.get('status')
    sub_type = await r.get('sub_type')
    now = time_with_tz()
    status = to_int_or_none(status)
    end_date = await r.get('end_date')
    start_date = await r.get('start_date')
    electricity_status_text = ""

    off_time = datetime.datetime.fromtimestamp(float(await r.get("off_time")))
    on_time = datetime.datetime.fromtimestamp(float(await r.get("on_time")))

    tz_info_off_time = off_time.tzinfo
    tz_info_on_time = on_time.tzinfo

    if status == 1:
        electricity_status_text += ("💡Світло є! \n"
                                    "Совіньйон 1, Ольгіївська")
        time_av = (f"Світло присутнє протягом: \n"
                   f"{time_format((now.replace(tzinfo=tz_info_on_time) - on_time).total_seconds())} \n"
                   f"Увімкнено о {on_time.strftime('%H:%M:%S %d.%m')}")
    else:
        electricity_status_text += ("⚫️Світла немає! \n"
                                    "Совіньйон 1, Ольгіївська")
        time_av = (f"Світло відсутнє протягом: \n"
                   f"{time_format((now.replace(tzinfo=tz_info_off_time) - off_time).total_seconds())} \n"
                   f"Вимкнено о {off_time.strftime('%H:%M:%S %d.%m')}")

    if sub_type == "":
        sub_type = "Наразі відключень НЕМАЄ"

    current_hour = time_with_tz().hour
    current_weekday = time_with_tz().weekday()
    current_cell = current_hour + current_weekday * 24

    zone_list: list[Zone] = get_next_zones(zones, current_cell)

    msg_text = (f"<b>{electricity_status_text}</b> \n"
                f"{time_av} \n")

    use_schedules = to_int_or_none(await r.get("enable_schedule"))

    if use_schedules:
        msg_text += (f"---------------------\n"
                     f"Зараз {zone_to_string(zones[current_cell])[0]} \n"
                     f"---------------------\n")

        for zone in zone_list:
            msg_text += (f"До {zone.zone_name[1]} о {zone.time}: \n"
                         f"{zone.time_left} \n")
        msg_text += "---------------------\n"
    else:
        msg_text += "\n"

    msg_text += (f"Останні дані з ДТЕКу: \n"
                 f"<i>{sub_type}</i> \n"
                 f"Оновлено о: {dtek_last_update} ")

    if start_date != "":
        msg_text += ("\n"
                     f"Вимкнення о {start_date}")
    if end_date != "":
        msg_text += ("\n\n"
                     f"<b>Відновлення о {end_date}</b>")

    msg_text += ("\n\n"
                 f"<a href='{DONATE_LINK}'>До чаю</a>")

    prev_msg_text: str = await r.get('prev_msg_text')
    if (prev_msg_text is None) or (msg_text == prev_msg_text):
        logger.debug("same or none, skipped...")
    else:
        await b.edit_message_text(msg_text, chat_id=MY_ID, message_id=msg_to_edit)
    await r.set('prev_msg_text', msg_text)


async def set_start_values():
    on_time = await r.get("on_time")
    off_time = await r.get("off_time")
    pause = await r.get("pause")
    send_request = await r.get("send_request")
    last_ping_update = await r.get("last_ping_update")

    now = datetime.datetime.now().timestamp()
    if not on_time:
        await r.set("on_time", now)
    if not off_time:
        await r.set("off_time", now)
    if not pause:
        await r.set("pause", 0)
    if not last_ping_update:
        await r.set("last_ping_update", str(now))
    if not send_request:
        await r.set("send_request", 0)


async def main():
    job_lock = asyncio.Lock()
    await bot.delete_webhook()
    await set_start_values()
    msg_to_edit = await r.get("edit_msg_id")
    if msg_to_edit is None:
        await send_notification(bot, first_start=True)
    scheduler = AsyncIOScheduler()

    await dtek_checker(r)
    await msg_editor(bot, job_lock)
    scheduler.add_job(check_electricity_change, 'interval', seconds=1, id='checker', args=(job_lock,))
    scheduler.add_job(dtek_checker, 'interval', seconds=DTEK_UPDATE_INTERVAL, jitter=20, args=(r,))
    scheduler.add_job(msg_editor, 'interval', seconds=MSG_UPDATE_INTERVAL, args=(bot, job_lock), id='editor')
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
