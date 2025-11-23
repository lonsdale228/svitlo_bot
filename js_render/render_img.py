import asyncio
import datetime
from zoneinfo import ZoneInfo

import imgkit

from get_dtek_timetable import get_raw_dtek_timetable

OFF_ICON = (
    "file:///F:/Users/Administrator/PycharmProjects/svitlo_bot/js_render/elec-off.svg"
)


async def get_today_tomorrow_timetable() -> tuple[dict, dict]:
    timetable_model = await get_raw_dtek_timetable()

    today_timetable = {}
    tomorrow_timetable = {}

    for key, val in timetable_model["data"].items():
        dtek_time = datetime.datetime.fromtimestamp(
            int(key), tz=ZoneInfo("Europe/Kyiv")
        )
        if dtek_time.date() == datetime.datetime.now().date():
            today_timetable = val["GPV4.2"]
        else:
            tomorrow_timetable = val["GPV4.2"]
    return today_timetable, tomorrow_timetable


async def to_img(today: dict, tomorrow: dict, name: str):
    options = {
        "enable-local-file-access": None,
        "width": "0"
    }

    def build_table(schedule: dict) -> str:
        html = ""
        # FIRST ROW: 00–12
        html += "<table><tr>\n"
        for h in range(0, 12):
            html += f"<th>{h:02d}-{h+1:02d}</th>\n"
        html += "</tr>\n<tr>\n"

        for idx in range(1, 13):
            status = schedule[str(idx)]
            if status == "yes":
                html += "<td class='yes'></td>\n"
            elif status == "no":
                html += f"<td class='no'><img class='icon-off' src='{OFF_ICON}'></td>\n"
            elif status == "first":
                html += f"<td class='first'><img class='icon-off' src='{OFF_ICON}'></td>\n"
            else:
                html += f"<td class='second'><img class='icon-off' src='{OFF_ICON}'></td>\n"
        html += "</tr>\n"

        # SECOND ROW: 12–24
        html += "<tr>\n"
        for h in range(12, 24):
            html += f"<th>{h:02d}-{h + 1:02d}</th>\n"
        html += "</tr>\n<tr>\n"

        for idx in range(13, 25):
            status = schedule[str(idx)]
            if status == "yes":
                html += "<td class='yes'></td>\n"
            elif status == "no":
                html += f"<td class='no'><img class='icon-off' src='{OFF_ICON}'></td>\n"
            elif status == "first":
                html += f"<td class='first'><img class='icon-off' src='{OFF_ICON}'></td>\n"
            else:
                html += f"<td class='second'><img class='icon-off' src='{OFF_ICON}'></td>\n"
        html += "</tr></table>"

        return html

    table_today = build_table(today)
    table_tomorrow = build_table(tomorrow)

    html = f"""
<html>
<head>
<style>
body {{
    background: white;
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 10;
}}

table {{
    border-collapse: collapse;
    background: white;
    margin-bottom: 10px;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 10px 8px;
    text-align: center;
    min-width: 50px;
    font-size: 16px;
}}

th {{
    background: #4CAF50;
    color: white;
    font-weight: bold;
}}

.yes {{
    font-size: 22px;
    font-weight: bold;
    color: #0a8a0a;
}}

.no {{
    font-size: 22px;
    font-weight: bold;
    background: lightgray;
}}

.icon-off {{
    width: 24px;
    height: 24px;
}}

.first::before,
.second::before {{
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    width: 2px;
    left: 50%;
    background: rgba(0,0,0,0.6);
    z-index: 3;
}}

.first::after,
.second::after {{
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    width: 50%;
    background: rgba(0,0,0,0.15);
    z-index: 1;
}}

.first::after {{ left: 0; }}
.second::after {{ right: 0; }}

.first, .second {{
    position: relative;
    padding-left: 8px;
    padding-right: 8px;
}}

.title {{
    font-size: 26px;
    font-weight: bold;
    margin: 20px 0 10px 0;
}}
</style>
</head>
<body>

<div class="title">Графік на сьогодні:</div>
{table_today}

<div class="title">Графік на завтра:</div>
{table_tomorrow}

</body>
</html>
"""

    imgkit.from_string(html, f"gpv42_schedule_{name}.png", options=options)

async def timetable_to_img():
    today, tomorrow = await get_today_tomorrow_timetable()
    await to_img(today, tomorrow, "combined")


if __name__ == "__main__":
    asyncio.run(timetable_to_img())