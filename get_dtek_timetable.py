import asyncio
import datetime
import json
import re
from typing import Any, Coroutine
from zoneinfo import ZoneInfo

import aiohttp


dtek_url = "https://www.dtek-oem.com.ua/ua/shutdowns"

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "X-Csrf-Token": "gJASGCjYpQvg7GGEDT4eIueld_RnbGIshdRB5sH4ZijGpmBbd5L2XJavKd00DlNsodUbkiAWUH7C7HaoicsEag==",
    "X-Requested-With": "XMLHttpRequest",
}


def convert_dtek_dict_to_time_ranges(dtek_dict: dict) -> list[str]:
    result = []

    current_no_start = None
    previous_hour_was_no = False

    for hour_str, status in dtek_dict.items():
        hour = int(hour_str)
        next_hour = hour + 1

        if status == "no":
            if not previous_hour_was_no:
                current_no_start = hour
            previous_hour_was_no = True
            continue

        if previous_hour_was_no:
            result.append(f"з {current_no_start}:00 по {hour}:00")
            previous_hour_was_no = False

        if status == "first":
            result.append(f"з {hour}:00 по {hour}:30")

        elif status == "second":
            result.append(f"з {hour}:30 по {next_hour}:00")

    if previous_hour_was_no:
        result.append(f"з {current_no_start}:00 по {hour + 1}:00")

    return result


async def get_dtek_timetable() -> tuple[list[str], list[str], str]:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(dtek_url, headers=headers) as response:
            html = await response.text()

            pattern = r"DisconSchedule\.fact\s*=\s*({.*})"
            match = re.search(pattern, html, flags=re.S)
            if not match:
                raise ValueError("JSON not found inside last <script>")

            json_text = match.group(1)
            data = json.loads(json_text)

            now = datetime.datetime.now(tz=ZoneInfo("Europe/Kyiv"))
            for key, val in data["data"].items():
                dtek_time = datetime.datetime.fromtimestamp(
                    int(key), tz=ZoneInfo("Europe/Kyiv")
                )
                if dtek_time.date() == now.date():
                    converted_ranges_today = convert_dtek_dict_to_time_ranges(val["GPV4.2"])
                else:
                    converted_ranges_tomorrow = convert_dtek_dict_to_time_ranges(
                        val["GPV4.2"]
                    )

            last_update_time: str = data["update"]
            return converted_ranges_today, converted_ranges_tomorrow, last_update_time


if __name__ == "__main__":
    asyncio.run(get_dtek_timetable())