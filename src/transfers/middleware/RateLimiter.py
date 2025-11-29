from quart import Request, Response, current_app, abort
import time
from logging import getLogger

logger = getLogger(__name__)

class RateLimiter:
    def __init__(self, app, limit=50, window=60):
        self.app = app
        self.limit = limit
        self.window = window
        self.app.before_request(self.check_limit)

    async def check_limit(self):
        redis = getattr(self.app, 'redis_client', None)
        if not redis:
            logger.warning("Redis client not available for Rate Limiter")
            return

        client_ip = "unknown"
        if request := getattr(current_app, 'request', None):
             if request.remote_addr:
                 client_ip = request.remote_addr

        current_minute = int(time.time() // self.window)
        key = f"rate_limit:{client_ip}:{current_minute}"

        current_count = 0
        try:
            current_count = await redis.incr(key)
            if current_count == 1:
                await redis.expire(key, self.window)
        except Exception as e:
            logger.error(f"Rate limiter Redis error: {e}")
            return

        if current_count > self.limit:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            abort(429, description="Too Many Requests")
