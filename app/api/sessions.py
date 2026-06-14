"""Session management API routes."""

from fastapi import APIRouter

from fastapi import HTTPException

from app.db.crud import delete_session, list_session_messages, list_sessions, rename_session
from app.schemas.session import SessionMessage, SessionRenameRequest, SessionSummary

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionSummary])
def get_sessions() -> list[SessionSummary]:
    """List user-facing sessions; test/eval sessions are hidden by CRUD logic."""
    return [SessionSummary(**item) for item in list_sessions()]


@router.get("/{session_id}/messages", response_model=list[SessionMessage])
def get_session_messages(session_id: str) -> list[SessionMessage]:
    """Return all messages for a session in chronological order."""
    return [SessionMessage(**item) for item in list_session_messages(session_id)]


@router.patch("/{session_id}", response_model=SessionSummary)
def update_session(session_id: str, req: SessionRenameRequest) -> SessionSummary:
    """Rename a session and return its updated summary."""
    renamed = rename_session(session_id, req.title)
    if not renamed:
        raise HTTPException(status_code=400, detail="Session title cannot be empty.")
    for item in list_sessions():
        if item["session_id"] == session_id:
            return SessionSummary(**item)
    raise HTTPException(status_code=404, detail="Session not found.")


@router.delete("/{session_id}")
def remove_session(session_id: str) -> dict[str, bool]:
    """Delete a session, including messages and tool traces via ORM cascade."""
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True}
