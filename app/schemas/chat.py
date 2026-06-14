"""Pydantic schemas for chat requests and responses."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A source snippet used to explain a RAG answer."""

    source: str
    snippet: str


class ToolTrace(BaseModel):
    """One tool invocation shown in the UI trace panel."""

    tool_name: str
    tool_input: str
    tool_output: str


class ChatRequest(BaseModel):
    """Incoming chat request from the frontend."""

    message: str = Field(..., min_length=1)
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Structured response returned by the Agent."""

    answer: str
    session_id: str
    used_tools: list[ToolTrace] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    need_human: bool = False
    handoff_reason: str | None = None
