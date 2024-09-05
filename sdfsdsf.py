import os

import redis

if os.name == 'nt':
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8")
else:
    r = redis.from_url("redis://redis:6379", encoding="utf8")

r.set("status", int(True))
