import os
import redis
from typing import Optional

class LocalVault:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.pool = redis.ConnectionPool(
            host=os.getenv("REDIS_HOST", host),
            port=port,
            db=db,
            max_connections=20,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def ping(self) -> bool:
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False

    def set_mapping(self, token_key: str, original_value: str, ttl_seconds: int = 3600) -> bool:
        return self.client.setex(name=token_key, time=ttl_seconds, value=original_value)

    def get_mapping(self, token_key: str) -> Optional[str]:
        return self.client.get(token_key)

    def delete_mapping(self, token_key: str) -> int:
        return self.client.delete(token_key)