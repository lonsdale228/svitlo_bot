import asyncio
import os
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
app = FastAPI()

API_KEY = os.getenv("API_KEY")
@app.on_event("startup")
async def startup():
    if os.name == 'nt':
        redis_connection = redis.from_url("redis://127.0.0.1:6379", encoding="utf-8", decode_responses=True)
    else:
        redis_connection = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)


if os.name == 'nt':
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8", decode_responses=True)
else:
    r = redis.from_url("redis://redis:6379", encoding="utf8", decode_responses=True)


class StatusRequest(BaseModel):
    status: str


@app.get("/get_status", dependencies=[Depends(RateLimiter(times=60, seconds=60))])
async def get_status():
    status = await r.get("status")
    return status


@app.post("/send_status", dependencies=[Depends(RateLimiter(times=100, seconds=60))])
async def send_status(request: StatusRequest, req: Request):
    api_key = req.headers.get('X-API-Key')
    if api_key == API_KEY:
        status = request.status
        if status == "on":
            print("now is enable")
            await r.set("status", 1)
        if status == "off":
            print("now is disable")
            await r.set("status", 0)
        return {"message": "Status received", "status": status}
    else:
        return {"message": "API key not available"}


async def run():
    config = uvicorn.Config(app, host="0.0.0.0", port=1889, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(run())
