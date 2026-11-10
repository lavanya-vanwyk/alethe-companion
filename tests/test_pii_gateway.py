import re
from unittest.mock import AsyncMock

import pytest

from src.application.pii_gateway import PIIGateway
from src.domain.entities import MemoryPointer
from src.infrastructure.pii_scanners import RegexScannerAdapter

# AWS's documented example key, not a real credential
EXAMPLE_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
TOKEN_PATTERN = r"\{\{(?:EMAIL|AWS_KEY)_[0-9A-F]{6}\}\}"


@pytest.fixture
def mock_vault():
    vault = AsyncMock()
    vault.store_mapping = AsyncMock(return_value=True)
    return vault


@pytest.fixture
def gateway(mock_vault):
    return PIIGateway(vault=mock_vault, scanner=RegexScannerAdapter())


def test_scanner_detects_default_types():
    """Verifies the default rules classify emails and AWS keys."""
    matches = RegexScannerAdapter().scan(f"dev@example.com uses {EXAMPLE_AWS_KEY}")

    found = {(m.pii_type, m.original_value) for m in matches}
    assert ("EMAIL", "dev@example.com") in found
    assert ("AWS_KEY", EXAMPLE_AWS_KEY) in found


@pytest.mark.asyncio
async def test_tokenize_scrubs_payload_and_stores_mappings(gateway, mock_vault):
    """Verifies sensitive values are replaced and their mappings sent to the vault."""
    payload = f"Email dev@example.com with key {EXAMPLE_AWS_KEY}"

    result = await gateway.tokenize_payload(payload)

    assert "dev@example.com" not in result
    assert EXAMPLE_AWS_KEY not in result
    assert re.fullmatch(f"Email {TOKEN_PATTERN} with key {TOKEN_PATTERN}", result)

    stored = {
        call.args[0].pointer_key: call.args[0].content
        for call in mock_vault.store_mapping.call_args_list
    }
    assert sorted(stored.values()) == sorted(["dev@example.com", EXAMPLE_AWS_KEY])
    for token in re.findall(TOKEN_PATTERN, result):
        assert token in stored


@pytest.mark.asyncio
async def test_tokenize_reuses_token_for_repeated_value(gateway, mock_vault):
    """Verifies a value appearing twice maps to one token and one vault entry."""
    result = await gateway.tokenize_payload("dev@example.com and dev@example.com")

    tokens = re.findall(TOKEN_PATTERN, result)
    assert len(tokens) == 2 and tokens[0] == tokens[1]
    mock_vault.store_mapping.assert_called_once()
    pointer: MemoryPointer = mock_vault.store_mapping.call_args.args[0]
    assert pointer.pointer_key == tokens[0]


@pytest.mark.asyncio
async def test_tokenize_leaves_clean_payload_untouched(gateway, mock_vault):
    """Verifies payloads without PII pass through and nothing is stored."""
    payload = "def add(a, b): return a + b"

    assert await gateway.tokenize_payload(payload) == payload
    mock_vault.store_mapping.assert_not_called()
