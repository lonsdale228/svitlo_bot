import time
from datetime import datetime

import redis

# Connect to the Redis server
r = redis.Redis(host='localhost', port=6379, db=0)


while True:
    key = r.get('now_time').decode()
    print(key)
    time.sleep(1)