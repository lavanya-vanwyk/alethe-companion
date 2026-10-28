from pydantic import BaseModel, Field
from typing import List, Optional

class MemoryPointer(BaseModel):
    """Represents a tokenized reference to sensitive data or large AST blocks."""
    pointer_key: str = Field(..., description="The synthetic token (e.g., {{TOKEN_A1}} or {{REF_AST_AUTH}})")
    content: str = Field(..., description="The original underlying data or codebase text")
    ttl_seconds: int = 3600

class CodeChangeDelta(BaseModel):
    """Represents structural codebase changes captured via AST parsing."""
    file_path: str
    changed_lines: List[int]
    structural_summary: str = Field(..., description="AST-derived summary of structural changes (e.g., 'Method X abstracted')")

class SessionState(BaseModel):
    """Tracks the lifecycle and TTL of the active CLI session."""
    session_id: str
    active_model: str
    current_turns: int = 0
    max_turns: int = 10
    global_roadmap: str = ""
    
    def increment_turn(self) -> None:
        self.current_turns += 1

    def is_ttl_reached(self) -> bool:
        return self.current_turns >= self.max_turns
        
    def reset_ttl(self) -> None:
        self.current_turns = 0