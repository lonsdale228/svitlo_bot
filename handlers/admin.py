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


@router.message(Command("pause_request"))
async def pause_request_bot(message: Message):
    await r.set("send_request", 0)
    await message.answer("Requests paused!")


@router.message(Command("resume_request"))
async def resume_request_bot(message: Message):
    await r.set("send_request", 1)
    await message.answer("Requests resumed!")


@router.message(Command("last_ping_update"))
async def last_update_bot(message: Message):
    last_update_time: datetime.datetime = datetime.datetime.fromtimestamp(float(await r.get("last_ping_update")))
    await message.answer(last_update_time.strftime("%Y-%m-%d %H:%M:%S"))


@router.message(Command("disable_schedule"))
async def disable_schedule_bot(message: Message):
    await r.set("enable_schedule", 0)
    await message.answer("Schedule disabled!")


@router.message(Command("enable_schedule"))
async def disable_schedule_bot(message: Message):
    await r.set("enable_schedule", 1)
    await message.answer("Schedule enabled!")


@router.message(Command("status"))
async def status_bot(message: Message):
    status = await r.get("status")
    last_update_time: datetime.datetime = datetime.datetime.fromtimestamp(float(await r.get("last_ping_update")))
    now = datetime.datetime.now()
    api_uniq_user_count = await r.scard("api_users")

    await message.answer(f"Світло: {status} \n"
                         f"Last request: {last_update_time} \n"
                         f"{(now - last_update_time).total_seconds()} ago \n"
                         f"Uniq_user_count: {api_uniq_user_count}")
