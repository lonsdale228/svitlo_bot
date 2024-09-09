import os

import redis.asyncio as redis
if os.name == 'nt':
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8", decode_responses=True)
else:
    r = redis.from_url("redis://redis:6379", encoding="utf8", decode_responses=True)