"""Runtime Agent state.

The database keeps persistent history. This in-memory store only helps the
current process reuse recent context while a session is active.
"""

from pydantic import BaseModel, Field

from app.schemas.chat import ToolTrace


class AgentState(BaseModel):
    """Mutable state passed through one chat session."""

    session_id: str
    messages: list[dict[str, str]] = Field(default_factory=list)
    tool_traces: list[ToolTrace] = Field(default_factory=list)


SESSION_STORE: dict[str, AgentState] = {}


def get_or_create_state(session_id: str) -> AgentState:
    """Return existing runtime state, or create it on first access."""
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = AgentState(session_id=session_id)
    return SESSION_STORE[session_id]
