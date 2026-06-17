"""Agent 运行时状态管理。

数据库负责持久化历史记录。这里的内存存储仅在当前进程中缓存活跃会话的
近期上下文，避免每轮对话都查询数据库。
"""

from pydantic import BaseModel, Field

from app.schemas.chat import ToolTrace


class AgentState(BaseModel):
    """单个聊天会话的可变运行时状态。

    Attributes:
        session_id: 会话唯一标识
        messages: 本次进程内积累的消息历史（内存缓存）
        tool_traces: 本次进程内的工具调用追踪记录
    """

    session_id: str
    messages: list[dict[str, str]] = Field(default_factory=list)
    tool_traces: list[ToolTrace] = Field(default_factory=list)


# 进程级会话状态存储，key 为 session_id
SESSION_STORE: dict[str, AgentState] = {}


def get_or_create_state(session_id: str) -> AgentState:
    """获取已有的运行时状态，首次访问时自动创建。

    这是一个简单的进程内缓存，重启后状态丢失，
    持久化数据由数据库层保证。
    """
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = AgentState(session_id=session_id)
    return SESSION_STORE[session_id]
