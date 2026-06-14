"""Application service for chat requests."""

from uuid import uuid4

from app.agent.runner import run_agent
from app.agent.state import get_or_create_state
from app.db.crud import ensure_session, get_recent_messages
from app.schemas.chat import ChatRequest, ChatResponse


def handle_chat(req: ChatRequest) -> ChatResponse:
    """Prepare session state, load persisted history, and run one Agent turn."""
    session_id = req.session_id or str(uuid4())
    ensure_session(session_id)
    state = get_or_create_state(session_id)
    if not state.messages:
        state.messages = get_recent_messages(session_id)
    return run_agent(req.message, state)
