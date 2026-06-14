from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    snippet: str


class ToolTrace(BaseModel):
    tool_name: str
    tool_input: str
    tool_output: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    used_tools: list[ToolTrace] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    need_human: bool = False
    handoff_reason: str | None = None
