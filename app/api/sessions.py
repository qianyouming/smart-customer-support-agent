"""会话管理 API 路由。

提供会话列表、消息查看、重命名和删除功能，供前端侧边栏使用。
"""

from fastapi import APIRouter

from fastapi import HTTPException

from app.db.crud import delete_session, list_session_messages, list_sessions, rename_session
from app.schemas.session import SessionMessage, SessionRenameRequest, SessionSummary

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionSummary])
def get_sessions() -> list[SessionSummary]:
    """列出用户可见的会话；测试/评测会话已被 CRUD 层自动过滤。"""
    return [SessionSummary(**item) for item in list_sessions()]


@router.get("/{session_id}/messages", response_model=list[SessionMessage])
def get_session_messages(session_id: str) -> list[SessionMessage]:
    """返回指定会话的所有消息，按时间正序排列。"""
    return [SessionMessage(**item) for item in list_session_messages(session_id)]


@router.patch("/{session_id}", response_model=SessionSummary)
def update_session(session_id: str, req: SessionRenameRequest) -> SessionSummary:
    """重命名会话并返回更新后的摘要。"""
    renamed = rename_session(session_id, req.title)
    if not renamed:
        raise HTTPException(status_code=400, detail="Session title cannot be empty.")
    for item in list_sessions():
        if item["session_id"] == session_id:
            return SessionSummary(**item)
    raise HTTPException(status_code=404, detail="Session not found.")


@router.delete("/{session_id}")
def remove_session(session_id: str) -> dict[str, bool]:
    """删除会话及关联数据（消息和工具调用通过 ORM 级联删除）。"""
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True}
