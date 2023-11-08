from celery.app import Celery
import redis
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
rd = redis.Redis(host='localhost', port=6379, decode_responses=True)
app = Celery(__name__, broker=redis_url, backend=redis_url, include=[
    'worker.garch',
    'worker.gp',
    'worker.mc',
])
