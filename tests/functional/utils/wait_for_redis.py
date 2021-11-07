import os
import time

from redis import Redis

timeout = time.time() + 60 * 5  # 5 minutes from now
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis = Redis(host=REDIS_HOST, port=REDIS_PORT)

ping = False
while ping == False:
    try:
        ping = redis.ping()
    except:
        pass
    print(str("Redis Alive:" + str(ping)))
