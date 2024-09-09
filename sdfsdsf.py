import os
import random
import time

import redis

if os.name == 'nt':
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8")
else:
    r = redis.from_url("redis://redis:6379", encoding="utf8")

# for _ in range(10_000):
#     time.sleep(random.randint(1, 30))
#     stat = int(r.get("status"))
#     status = 0 if stat == 1 else 1
#     r.set("status", status)

stat = r.get('status')
print(stat)
