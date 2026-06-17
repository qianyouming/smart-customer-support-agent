"""聊天请求的应用服务层。

作为 API 路由和 Agent 运行器之间的协调层，负责：
1. 确定或生成 session_id
2. 确保数据库中有对应的会话记录
3. 加载/恢复运行时状态
4. 调用 Agent 执行一轮对话
"""

from uuid import uuid4

from app.agent.runner import run_agent
from app.agent.state import get_or_create_state
from app.db.crud import ensure_session, get_recent_messages
from app.schemas.chat import ChatRequest, ChatResponse


def handle_chat(req: ChatRequest) -> ChatResponse:
    """处理一次聊天请求：准备状态 → 加载历史 → 执行 Agent → 返回结果。

    如果请求未指定 session_id，会自动生成一个新的 UUID。
    首次对话时从数据库加载持久化的历史消息到内存状态中。
    """
    session_id = req.session_id or str(uuid4())
    ensure_session(session_id)
    state = get_or_create_state(session_id)
    # 首次访问该会话时，从数据库恢复历史消息到内存
    if not state.messages:
        state.messages = get_recent_messages(session_id)
    return run_agent(req.message, state)
