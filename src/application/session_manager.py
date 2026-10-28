from src.domain.entities import SessionState

class SessionManager:
    """Orchestrates the chat session, acting as the primary Application Service."""
    
    def __init__(self, default_model: str = "ollama"):
        self.state = SessionState(session_id="default-session", active_model=default_model)

    def switch_model(self, new_model: str) -> None:
        """Updates the active model in the domain state."""
        self.state.active_model = new_model

    def process_input(self, user_input: str) -> str:
        """
        Handles the core loop logic per turn.
        Placeholder for LLM routing and Context Engine logic in Sprint 3.
        """
        self.state.increment_turn()
        
        # Check TTL constraint from domain entity
        if self.state.is_ttl_reached():
            # Placeholder for RAG Rollover in Sprint 4
            self.state.reset_ttl()
            return "[System] TTL limit reached. Triggering state compression (Mocked)..."
            
        return f"[Mock] Processed '{user_input}' (Turn: {self.state.current_turns}/{self.state.max_turns})"