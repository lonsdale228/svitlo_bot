from main import r



async def api_key_check(value):
    if value in (await r.lrange('api_keys', 0, -1)):
        return True
    else:
        return False
