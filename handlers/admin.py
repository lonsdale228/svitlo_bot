from aiogram import Router, F
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message
import datetime
from redis_loader import r

admin_ids = [317465871]


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admin_ids


router = Router(name=__name__)
router.message.filter(IsAdminFilter())


@router.message(Command("pause"))
async def pause_bot(message: Message):
    await r.set("pause", 1)
    await message.answer("Bot paused!")


@router.message(Command("resume"))
async def resume_bot(message: Message):
    await r.set("pause", 0)
    await message.answer("Bot resumed!")


@router.message(Command("last_ping_update"))
async def last_update_bot(message: Message):
    last_update_time: datetime.datetime = await r.get("last_ping_update")
    await message.answer(last_update_time.strftime("%Y-%m-%d %H:%M:%S"))
