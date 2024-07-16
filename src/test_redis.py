import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# redis.from_url
r.set("phone_number", "+79045530790")
num = r.get("phone_number")

print(num)

pipe = r.pipeline().hset()
