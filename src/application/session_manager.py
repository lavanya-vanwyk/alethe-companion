from src.application.pii_gateway import PIIGateway
from src.domain.entities import SessionState
from src.domain.ports import GitTrackerPort


class SessionManager:
    """Orchestrates the chat session, acting as the primary Application Service."""

    def __init__(
        self,
        pii_gateway: PIIGateway | None = None,
        git_tracker: GitTrackerPort | None = None,
        default_model: str = "ollama",
    ):
        self.state = SessionState(
            session_id="default-session", active_model=default_model
        )
        self.pii_gateway = pii_gateway
        self.git_tracker = git_tracker

    def switch_model(self, new_model: str) -> None:
        self.state.active_model = new_model

    def process_input(self, user_input: str) -> str:
        """
        Handles the core loop logic per turn.
        Placeholder for LLM routing and Context Engine logic in Sprint 3.
        """
        self.state.increment_turn()

        if user_input.strip().lower() == "/diff" and self.git_tracker:
            deltas = self.git_tracker.get_structural_diffs()
            if not deltas:
                return "[System] No staged Python changes detected in Git."

            output = "[System] Current Staged AST Diffs:\n"
            for d in deltas:
                output += f"- {d.file_path}: {d.structural_summary} (Lines: {d.changed_lines})\n"
            return output

        # Check TTL constraint from domain entity
        if self.state.is_ttl_reached():
            self.state.reset_ttl()
            return (
                "[System] TTL limit reached. Triggering state compression (Mocked)..."
            )

        return f"[Mock] Processed '{user_input}' (Turn: {self.state.current_turns}/{self.state.max_turns})"
