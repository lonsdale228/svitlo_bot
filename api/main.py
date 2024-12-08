import asyncio
import datetime
import os
from contextlib import asynccontextmanager
from math import ceil

import pytz
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


TIMEZONE = 'Europe/Kyiv'

API_KEY = os.getenv("API_KEY")

@asynccontextmanager
async def lifespan(_: FastAPI):

    if os.name == 'nt':
        redis_connection = redis.from_url("redis://127.0.0.1:6379", encoding="utf-8", decode_responses=True)
    else:
        redis_connection = redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)

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


@app.get("/get_status", dependencies=[Depends(RateLimiter(times=1, seconds=9))])
async def get_status(req: Request):
    stat = await r.get("status")
    return stat


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
