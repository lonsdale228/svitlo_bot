import os

import redis.asyncio as redis

username = os.getenv("REDIS_USERNAME")
password = os.getenv("REDIS_PASSWORD")
if os.name == 'nt':
    r = redis.from_url(f"redis://{username}:{password}@127.0.0.1:6379", encoding="utf8", decode_responses=True)
else:
    r = redis.from_url(f"redis://{username}:{password}@redis:6379", encoding="utf8", decode_responses=True)