"""会话相关的 Pydantic 数据模型。"""

from pydantic import BaseModel


class SessionSummary(BaseModel):
    """会话摘要：侧边栏中展示的单个会话信息。"""

    session_id: str
    title: str
    created_at: str | None = None
    updated_at: str | None = None
    message_count: int
    preview: str | None = None          # 最近一条消息的预览文本


class SessionMessage(BaseModel):
    """会话中的一条持久化消息。"""

    role: str                           # "user" 或 "assistant"
    content: str
    created_at: str


class SessionRenameRequest(BaseModel):
    """会话重命名请求体。"""

    title: str
