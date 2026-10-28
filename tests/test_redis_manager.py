import asyncio

from src.domain.entities import MemoryPointer
from src.infrastructure.redis_vault import RedisTokenVault


async def verify_async_crud():
    print("Initializing RedisTokenVault...")
    vault = RedisTokenVault()

    # Connection
    await vault.connect()
    is_connected = await vault.ping()
    print(f"Connection Status: {'SUCCESS' if is_connected else 'FAILED'}")

    if not is_connected:
        print(
            "Please ensure your local Redis server is running (e.g., docker run -p 6379:6379 -d redis)"
        )
        return

    # Create/Store
    test_pointer = MemoryPointer(
        pointer_key="{{TOKEN_TEST_KEY}}",
        content="super_secret_api_key_12345",
        ttl_seconds=10,
    )
    store_success = await vault.store_mapping(test_pointer)
    print(f"Store Mapping Status: {'SUCCESS' if store_success else 'FAILED'}")

    # Read/Retrieve
    retrieved_content = await vault.retrieve_mapping("{{TOKEN_TEST_KEY}}")
    print(
        f"Retrieved Content Matches: {'SUCCESS' if retrieved_content == test_pointer.content else 'FAILED'}"
    )

    await vault.disconnect()
    print("Test complete. Disconnected from Redis.")


if __name__ == "__main__":
    asyncio.run(verify_async_crud())
