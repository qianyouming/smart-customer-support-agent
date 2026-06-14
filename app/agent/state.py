from pydantic import BaseModel, Field

from app.schemas.chat import ToolTrace


class AgentState(BaseModel):
    session_id: str
    messages: list[dict[str, str]] = Field(default_factory=list)
    tool_traces: list[ToolTrace] = Field(default_factory=list)


SESSION_STORE: dict[str, AgentState] = {}


def get_or_create_state(session_id: str) -> AgentState:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = AgentState(session_id=session_id)
    return SESSION_STORE[session_id]

