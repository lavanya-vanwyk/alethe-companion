import pytest
from unittest.mock import AsyncMock, patch
from src.infrastructure.redis_vault import RedisTokenVault
from src.domain.entities import MemoryPointer

@pytest.fixture
def mock_redis_client():
    client = AsyncMock()
    client.setex = AsyncMock(return_value=True)
    client.get = AsyncMock(return_value="original_secret_data")
    return client

@pytest.mark.asyncio
async def test_vault_store_mapping(mock_redis_client):
    """Verifies the Vault correctly maps the Domain entity to the Redis client."""
    vault = RedisTokenVault()
    vault.client = mock_redis_client

    pointer = MemoryPointer(
        pointer_key="{{TOKEN_X1}}",
        content="original_secret_data",
        ttl_seconds=3600
    )

    success = await vault.store_mapping(pointer)
    
    assert success is True
    mock_redis_client.setex.assert_called_once_with(
        name="{{TOKEN_X1}}",
        time=3600,
        value="original_secret_data"
    )

@pytest.mark.asyncio
async def test_vault_retrieve_mapping(mock_redis_client):
    """Verifies the Vault correctly retrieves data based on a token key."""
    vault = RedisTokenVault()
    vault.client = mock_redis_client  # Inject mock client

    result = await vault.retrieve_mapping("{{TOKEN_X1}}")
    
    assert result == "original_secret_data"
    mock_redis_client.get.assert_called_once_with("{{TOKEN_X1}}")