import uuid

from src.domain.entities import MemoryPointer
from src.domain.ports import PIIScannerPort, TokenVaultPort


class PIIGateway:
    """
    Application service responsible for scanning payloads,
    swapping sensitive data for tokens, and persisting mappings.
    """

    def __init__(self, vault: TokenVaultPort, scanner: PIIScannerPort):
        # Depends on the domain interfaces
        self.vault = vault
        self.scanner = scanner

    async def tokenize_payload(self, payload: str) -> str:
        """Swaps each sensitive value for a synthetic token stored in the vault."""
        tokenized_payload = payload
        matches = self.scanner.scan(payload)

        # Deduplicate matches so a repeated value maps to a single token
        unique_matches = {m.original_value: m for m in matches}.values()

        # Replace longest values first so a value nested in another is not split
        for match in sorted(
            unique_matches, key=lambda m: len(m.original_value), reverse=True
        ):
            token_id = uuid.uuid4().hex[:6].upper()
            token_key = f"{{{{{match.pii_type}_{token_id}}}}}"

            pointer = MemoryPointer(pointer_key=token_key, content=match.original_value)

            await self.vault.store_mapping(pointer)
            tokenized_payload = tokenized_payload.replace(
                match.original_value, token_key
            )

        return tokenized_payload

    async def rehydrate_response(self, response: str) -> str:
        """
        Placeholder for SEC-203: Will intercept stream,
        fetch tokens from self.vault, and return original string.
        """
        return response
