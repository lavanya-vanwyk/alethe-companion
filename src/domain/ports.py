from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from src.domain.entities import CodeChangeDelta, MemoryPointer, SessionState


class TokenVaultPort(ABC):
    """Outbound port for local memory pointer storage (e.g., Redis)."""

    @abstractmethod
    async def store_mapping(self, pointer: MemoryPointer) -> bool:
        pass

    @abstractmethod
    async def retrieve_mapping(self, pointer_key: str) -> str | None:
        pass


class GitTrackerPort(ABC):
    """Outbound port for version control and AST monitoring."""

    @abstractmethod
    def get_structural_diffs(self) -> list[CodeChangeDelta]:
        pass


class VectorDBPort(ABC):
    """Outbound port for semantic roadmap retrieval (e.g., ChromaDB)."""

    @abstractmethod
    async def store_session_summary(self, session_id: str, summary: str) -> bool:
        pass

    @abstractmethod
    async def retrieve_relevant_context(
        self, current_diffs: list[CodeChangeDelta]
    ) -> list[str]:
        pass


class LLMRouterPort(ABC):
    """Outbound port for LLM interaction and tool calling."""

    @abstractmethod
    async def stream_response(
        self, prompt: str, state: SessionState
    ) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    async def generate_roadmap_summary(self, session_transcript: str) -> str:
        pass
