import time
import redis
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    ssl=os.getenv('REDIS_SSL') == 'True'
)

def rate_limit(key, limit, period):
    """
    Rate limits requests to prevent abuse of the API.
    """
    try:
        now = int(time.time())
        period_start = now - (now % period)
        redis_key = f"{key}:{period_start}"
        current_requests = int(redis_client.get(redis_key) or 0)

        redis_client.incr(redis_key)
        redis_client.expire(redis_key, period)

        logger.debug(f"Rate limit: {current_requests} requests for {key} in {period}s")

        if current_requests > limit:
            time_to_wait = period - (now - period_start)
            raise RateLimitExceededError(
                f"Rate limit: {limit}/{period} seconds", time_to_wait, current_requests
            )
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis error: {e}")
        raise RateLimitExceededError("Rate limiting failed.", 0, 0)


class RateLimitExceededError(Exception):
    """
    Custom exception for when the rate limit is exceeded.
    """
    def __init__(self, message, time_to_wait, current_requests):
        super().__init__(message)
        self.time_to_wait = time_to_wait
        self.current_requests = current_requests