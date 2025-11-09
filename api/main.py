import asyncio
import datetime
import os
from contextlib import asynccontextmanager

import pytz
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi import FastAPI, Request, Response

TIMEZONE = 'Europe/Kyiv'

API_KEY = os.getenv("API_KEY")

username = os.getenv("REDIS_USERNAME")
password = os.getenv("REDIS_PASSWORD")

@asynccontextmanager
async def lifespan(_: FastAPI):

    if os.name == 'nt':
        redis_connection = redis.from_url(f"redis://{username}:{password}@127.0.0.1:6379", encoding="utf-8", decode_responses=True)
    else:
        redis_connection = redis.from_url(f"redis://{username}:{password}@redis:6379", encoding="utf-8", decode_responses=True)

    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.close()

if os.name == 'nt':
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8", decode_responses=True)
else:
    r = redis.from_url("redis://redis:6379", encoding="utf8", decode_responses=True)




def time_with_tz():
    return datetime.datetime.now(tz=pytz.timezone(TIMEZONE))


class StatusRequest(BaseModel):
    status: str
    value: str


app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)

RATE_LIMIT = 100
BAN_DURATION = 600
RATE_LIMIT_WINDOW = 60

# @app.middleware("http")
# async def rate_limiter(request: Request, call_next):
#     user_id = request.client.host
#     ban_key = f"ban:{user_id}"
#     count_key = f"count:{user_id}"
#
#     is_banned = await r.get(ban_key)
#     if is_banned:
#         return Response(status_code=403, content="You are banned. Please wait 10 minutes.")
#
#     current_count = await r.incr(count_key)
#
#     if current_count == 1:
#         await r.expire(count_key, RATE_LIMIT_WINDOW)
#
#     if current_count > RATE_LIMIT:
#         await r.set(ban_key, "1", ex=BAN_DURATION)
#         return Response(status_code=403, content="You are banned. Please wait 10 minutes.")
#
#     response = await call_next(request)
#     return response

@app.get("/get_status", dependencies=[Depends(RateLimiter(times=1, seconds=9))])
async def get_status(req: Request):
    stat = await r.get("status")
    ip = req.client.host
    await r.sadd("api_users", ip)
    await r.expire("api_users", 60)
    return stat

@app.get("/get_full_status", dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def get_full_status(req: Request):

    ip = req.client.host
    await r.sadd("api_users", ip)
    await r.expire("api_users", 60)

    reason = await r.get("sub_type")
    on_time = await r.get("on_time")
    off_time = await r.get("off_time")
    last_dtek_update = await r.get("dtek_update_timestamp")
    start_date = await r.get("start_date")
    end_date = await r.get("end_date")
    stat = await r.get("status")
    return {
        "reason": reason,
        "on_time": on_time,
        "off_time": off_time,
        "last_dtek_update": last_dtek_update,
        "start_date": start_date,
        "end_date": end_date,
        "status": stat
    }

@app.post("/send_status", dependencies=[Depends(RateLimiter(times=100, seconds=60))])
async def send_status(request: StatusRequest, req: Request):
    api_key = req.headers.get('X-API-Key')
    if api_key == API_KEY:
        status = request.status
        value = request.value
        print(status, value)
        if status == "on":
            print("now is enable")
            await r.set("status", 1)
        if status == "off":
            print("now is disable")
            await r.set("status", 0)

        await r.set("last_ping_update", str(time_with_tz().timestamp()))
        return {"message": "Status received", "status": status}
    else:
        return {"message": "API key not available"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1889, log_level="info")
