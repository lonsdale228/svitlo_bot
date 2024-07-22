import asyncio
from loader import bot, dp, client, logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def check_electricity_change():
    current_status = await client.get('status').decode()
    prev_status = await client.get('prev_status').decode()

    if current_status != prev_status:
        await client.set('status', current_status)
        await send_notification()
    else:
        ...

async def checker():
    ...

async def send_notification():
    ...


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_electricity_change, 'interval', seconds=3)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
