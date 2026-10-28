import os

import redis.asyncio as aioredis

from src.domain.entities import MemoryPointer
from src.domain.ports import TokenVaultPort


class RedisTokenVault(TokenVaultPort):
    """Infrastructure implementation of the TokenVaultPort using async Redis."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_url = os.getenv("REDIS_URL", f"redis://{host}:{port}/{db}")
        self.pool: aioredis.ConnectionPool | None = None
        self.client: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Initializes the async connection pool."""
        self.pool = aioredis.ConnectionPool.from_url(
            self.redis_url, max_connections=20, decode_responses=True
        )
        self.client = aioredis.Redis(connection_pool=self.pool)

    async def disconnect(self) -> None:
        """Gracefully closes Redis connections."""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()

    async def ping(self) -> bool:
        """Verifies the connection to the Redis server."""
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except aioredis.ConnectionError:
            return False

    async def store_mapping(self, pointer: MemoryPointer) -> bool:
        """Stores a synthetic token mapping in Redis with a TTL."""
        if not self.client:
            raise RuntimeError("Redis client is not connected.")

        # Pydantic entity ensures strict typing
        return await self.client.setex(
            name=pointer.pointer_key, time=pointer.ttl_seconds, value=pointer.content
        )

    async def retrieve_mapping(self, pointer_key: str) -> str | None:
        """Retrieves the original payload or codebase block."""
        if not self.client:
            raise RuntimeError("Redis client is not connected.")
        return await self.client.get(pointer_key)
