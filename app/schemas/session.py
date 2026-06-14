"""Pydantic schemas for chat session APIs."""

from pydantic import BaseModel


class SessionSummary(BaseModel):
    """Sidebar summary of one session."""

    session_id: str
    title: str
    created_at: str | None = None
    updated_at: str | None = None
    message_count: int
    preview: str | None = None


class SessionMessage(BaseModel):
    """One persisted message in a session."""

    role: str
    content: str
    created_at: str


class SessionRenameRequest(BaseModel):
    """Request body for renaming a session."""

    title: str
