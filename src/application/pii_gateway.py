from src.domain.ports import TokenVaultPort


class PIIGateway:
    """
    Application service responsible for scanning payloads,
    swapping sensitive data for tokens, and persisting mappings.
    """

    def __init__(self, vault: TokenVaultPort):
        # Depends on the domain interface
        self.vault = vault

    async def tokenize_payload(self, payload: str) -> str:
        """
        Placeholder for SEC-201: Will scan payload with regex,
        store matches in self.vault, and return tokenized string.
        """
        return payload

    async def rehydrate_response(self, response: str) -> str:
        """
        Placeholder for SEC-203: Will intercept stream,
        fetch tokens from self.vault, and return original string.
        """
        return response
