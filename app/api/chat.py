"""聊天 API 路由。"""

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """处理一条用户消息，返回 Agent 的完整响应（含工具追踪和引用）。"""
    return handle_chat(req)
