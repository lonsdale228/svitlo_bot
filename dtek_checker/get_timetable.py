import asyncio
import json
import re

from aiogram.client.session import aiohttp
from redis import Redis
from bs4 import BeautifulSoup

url = 'https://www.dtek-oem.com.ua/ua/shutdowns'
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


async def get_raw_page():
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None


async def get_timetable_by_group(group_num: int | str):
    raw_page = await get_raw_page()
    # soup = BeautifulSoup(raw_page, 'html.parser')
    # script_tag = soup.find('script', string=re.compile(r'DisconSchedule\.preset\s*=\s*'))
    # script_content: str = script_tag.string

    script_content = raw_page

    pattern = 'DisconSchedule.preset = '
    start_index = script_content.find(pattern)
    end_index = script_content.find('DisconSchedule.showCurSchedule')

    new_string = script_content[start_index+len(pattern):end_index].strip()
    json_string = json.loads(new_string)

    group_graphic = json_string['data'][str(group_num)]
    every_hour_stat = []
    for weekday in group_graphic.values():
        for hour in weekday.values():
            every_hour_stat.append(hour)

    print(every_hour_stat)

asyncio.run(get_timetable_by_group(4))