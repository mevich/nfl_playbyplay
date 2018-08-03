import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_conn = redis.Redis(connection_pool=pool)