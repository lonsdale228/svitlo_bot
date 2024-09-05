import os

import redis

if os.name == 'nt':
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8")
else:
    r = redis.from_url("redis://redis:6379", encoding="utf8")

# for i in r.keys():
#     print(f"{i.decode()}: ", f"Val: ({r.get(i).decode()})")
#     print(type(r.get(i).decode()))
#     print("_____________________________________________________________________________")
#
# for key in r.scan_iter("prefix:*"):
#     r.delete(key)


print(r.get("sub_type"))