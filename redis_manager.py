import os
import redis.asyncio as aioredis
from typing import Optional

class RedisConnectionManager:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_url = os.getenv("REDIS_URL", f"redis://{host}:{port}/{db}")
        self.pool: Optional[aioredis.ConnectionPool] = None
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Initializes the async connection pool (e.g., during startup)."""
        self.pool = aioredis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=20,
            decode_responses=True
        )
        self.client = aioredis.Redis(connection_pool=self.pool)

    async def disconnect(self):

        if self.client:
            await self.client.aclose()
        if self.pool:
            await self.pool.disconnect()

    async def ping(self) -> bool:
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except aioredis.ConnectionError:
            return False