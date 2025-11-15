import os
import re

from pyrogram import Client, filters
from pyrogram.types import Message

from bot import DONATE_LINK
from loader import dtek_timetable_bot as bot
from ocr.cv import crop_img

dtek_chat_id = -1399067835  # @dtek_ua
regex_filter_city = r"оде[сщ].*граф"
my_id = int(os.getenv("CHANNEL_ID"))


@Client.on_message(
    filters.chat([dtek_chat_id, "me"]) & filters.regex(regex_filter_city, re.IGNORECASE)
)
async def on_monitor_msg(client: Client, message: Message):
    chat = await client.get_chat(message.chat.id)
    text = (
        "⚠️ " + message.caption.html + f' \n\n<a href="{message.link}">{chat.title}</a>'
    )
    text += f"\n\n<a href='{DONATE_LINK}'>До чаю</a>"
    if message.media_group_id:
        group = await client.get_media_group(message.chat.id, message.id)
        msg = group[-1]
        if msg.photo:
            file = await client.download_media(msg, in_memory=True)
            file.seek(0)
            cropped_img = crop_img(file)
            await bot.send_photo(chat_id=my_id, photo=cropped_img, caption=text)

