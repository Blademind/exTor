import redis
redis_host = "192.168.1.197"
redis_port = 6379
r = redis.StrictRedis(host=redis_host, port=redis_port)
print(b"torrent" != "cake")