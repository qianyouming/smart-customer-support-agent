from pydantic import BaseModel


class SessionSummary(BaseModel):
    session_id: str
    title: str
    created_at: str | None = None
    updated_at: str | None = None
    message_count: int
    preview: str | None = None


class SessionMessage(BaseModel):
    role: str
    content: str
    created_at: str


class SessionRenameRequest(BaseModel):
    title: str
