"""数据库 CRUD 操作模块。

本模块是持久化边界层，封装了会话、消息、文档、检索片段、
工具调用记录和评测报告的增删改查操作。

所有数据库交互集中于此，上层业务逻辑不直接操作 ORM 模型。
"""

import re
from collections.abc import Iterable
from datetime import datetime
from uuid import uuid4

from sqlalchemy import delete, func, select

from app.core.config import settings
from app.db.models import ChatSession, Document, DocumentChunk, EvalResult, EvalRun, Message, ToolCall
from app.db.session import get_db_session


# ============================================================
# 会话管理相关的内部工具函数
# ============================================================


def _is_test_session(session_id: str) -> bool:
    """判断是否为测试/评测会话，这类会话不显示在用户侧边栏中。"""
    lowered = session_id.lower()
    return (
        lowered.startswith("test")
        or lowered.startswith("eval")
        or "test" in lowered
        or "eval" in lowered
    )


def _default_session_title(session_id: str) -> str:
    """在首条用户消息到达前生成一个友好的默认标题。"""
    if session_id.startswith("demo-"):
        return f"新会话 {datetime.now():%m-%d %H:%M}"
    return "新的客服咨询"


def _title_from_message(content: str) -> str:
    """用首条用户消息内容自动生成会话标题（截取前28字符）。"""
    clean = " ".join(content.strip().split())
    if not clean:
        return "新的客服咨询"
    return clean[:28] + ("..." if len(clean) > 28 else "")


def _is_default_title(title: str | None) -> bool:
    """判断标题是否仍为系统生成的默认标题（用于决定是否自动更新）。"""
    if not title:
        return True
    return title.startswith("新会话") or title == "新的客服咨询" or title == "客服会话"


# ============================================================
# 会话 CRUD
# ============================================================
def ensure_session(session_id: str) -> None:
    """确保会话行存在，不存在则自动创建。

    这是一个幂等操作，多次调用安全无副作用。
    """
    with get_db_session() as db:
        if db.get(ChatSession, session_id) is None:
            db.add(
                ChatSession(
                    id=session_id,
                    title=_default_session_title(session_id),
                    is_test=_is_test_session(session_id),
                )
            )
            db.commit()


def add_message(session_id: str, role: str, content: str) -> int:
    """持久化一条消息，并在必要时更新会话标题和时间戳。

    逻辑：
    - 每条消息都更新会话的 updated_at
    - 首条用户消息会自动更新会话标题（替换默认标题）
    """
    ensure_session(session_id)
    with get_db_session() as db:
        record = Message(session_id=session_id, role=role, content=content)
        db.add(record)
        session = db.get(ChatSession, session_id)
        if session is not None:
            session.updated_at = datetime.now()
        # 首条用户消息自动成为会话标题
        if role == "user":
            if session is not None and _is_default_title(session.title):
                session.title = _title_from_message(content)
        db.commit()
        db.refresh(record)
        return record.id


def get_recent_messages(session_id: str, limit: int | None = None) -> list[dict[str, str]]:
    """加载最近的对话历史，用于构建 LLM 的上下文提示。"""
    ensure_session(session_id)
    limit = limit or settings.max_history_messages
    with get_db_session() as db:
        rows = db.scalars(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.id.desc())
            .limit(limit)
        ).all()
    return [{"role": row.role, "content": row.content} for row in reversed(rows)]


def list_sessions() -> list[dict[str, str | int | None]]:
    """返回侧边栏展示的会话摘要列表，按最近活动排序。

    自动过滤掉测试和评测会话，不展示给普通用户。
    """
    with get_db_session() as db:
        rows = db.execute(
            select(
                ChatSession.id,
                ChatSession.title,
                ChatSession.created_at,
                ChatSession.updated_at,
                func.count(Message.id),
                func.max(Message.content),
            )
            .join(Message, Message.session_id == ChatSession.id, isouter=True)
            .where(ChatSession.is_test.is_(False))
            .where(ChatSession.id.not_like("test%"))
            .where(ChatSession.id.not_like("eval%"))
            .group_by(ChatSession.id, ChatSession.title, ChatSession.created_at, ChatSession.updated_at)
            .order_by(ChatSession.updated_at.desc())
        ).all()

    return [
        {
            "session_id": session_id,
            "title": title or _default_session_title(session_id),
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
            "message_count": message_count,
            "preview": preview,
        }
        for session_id, title, created_at, updated_at, message_count, preview in rows
    ]


def rename_session(session_id: str, title: str) -> bool:
    """重命名会话；空标题会被拒绝并返回 False。"""
    clean_title = title.strip()
    if not clean_title:
        return False
    ensure_session(session_id)
    with get_db_session() as db:
        session = db.get(ChatSession, session_id)
        if session is None:
            return False
        session.title = clean_title[:120]
        db.commit()
        return True


def delete_session(session_id: str) -> bool:
    """删除会话及其关联的消息和工具调用（通过 ORM 级联）。"""
    with get_db_session() as db:
        session = db.get(ChatSession, session_id)
        if session is None:
            return False
        db.delete(session)
        db.commit()
        return True


def list_session_messages(session_id: str) -> list[dict[str, str]]:
    """返回指定会话的所有消息，按时间正序排列。"""
    ensure_session(session_id)
    with get_db_session() as db:
        rows = db.scalars(
            select(Message).where(Message.session_id == session_id).order_by(Message.id.asc())
        ).all()
    return [{"role": row.role, "content": row.content, "created_at": row.created_at.isoformat()} for row in rows]


# ============================================================
# 工具调用记录
# ============================================================


def add_tool_call(session_id: str, tool_name: str, tool_input: str, tool_output: str) -> int:
    """持久化一次工具调用记录，用于可追溯性和 UI 展示。"""
    ensure_session(session_id)
    with get_db_session() as db:
        record = ToolCall(
            session_id=session_id,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id


# ============================================================
# 文档和知识库管理
# ============================================================


def create_document(filename: str, chunks: Iterable[str], content_type: str = "text/plain") -> dict[str, str | int]:
    """存储文档及其分块，同名文件会被替换（覆盖上传）。

    流程：
    1. 生成唯一 document_id
    2. 删除同名旧文档及其片段（实现"覆盖上传"）
    3. 写入新文档元数据和所有片段
    """
    document_id = str(uuid4())
    chunk_list = list(chunks)
    with get_db_session() as db:
        # 覆盖同名旧文档
        old_ids = db.scalars(select(Document.id).where(Document.filename == filename)).all()
        if old_ids:
            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id.in_(old_ids)))
            db.execute(delete(Document).where(Document.id.in_(old_ids)))
        # 写入新文档
        db.add(Document(id=document_id, filename=filename, content_type=content_type))
        for index, chunk in enumerate(chunk_list):
            db.add(
                DocumentChunk(
                    id=f"{document_id}:{index}",
                    document_id=document_id,
                    chunk_index=index,
                    content=chunk,
                )
            )
        db.commit()
    return {"document_id": document_id, "filename": filename, "chunks_created": len(chunk_list)}


def delete_document(document_id: str) -> bool:
    """删除文档及其关联片段（ORM 级联删除）。"""
    with get_db_session() as db:
        document = db.get(Document, document_id)
        if document is None:
            return False
        db.delete(document)
        db.commit()
        return True


def list_documents() -> list[dict[str, str | int]]:
    """返回知识库文档摘要列表，供侧边栏展示。"""
    with get_db_session() as db:
        rows = db.execute(
            select(Document.id, Document.filename, func.count(DocumentChunk.id))
            .join(DocumentChunk, DocumentChunk.document_id == Document.id, isouter=True)
            .group_by(Document.id, Document.filename)
            .order_by(Document.created_at.desc())
        ).all()
    return [
        {"document_id": document_id, "filename": filename, "chunks_count": chunks_count}
        for document_id, filename, chunks_count in rows
    ]


def get_document_detail(document_id: str) -> dict[str, str | int | list[dict[str, str | int]]] | None:
    """返回文档元数据和所有片段内容，供详情页展示。"""
    with get_db_session() as db:
        document = db.get(Document, document_id)
        if document is None:
            return None

        chunks = db.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        ).all()

        return {
            "document_id": document.id,
            "filename": document.filename,
            "content_type": document.content_type,
            "chunks_count": len(chunks),
            "chunks": [
                {
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                }
                for chunk in chunks
            ],
        }


# ============================================================
# RAG 检索
# ============================================================


def _tokens(text: str) -> set[str]:
    """分词：提取英文单词/数字和中文双字词组，用于关键词匹配。

    这是一个简易的分词实现，通过正则匹配：
    - 英文单词和数字：[A-Za-z0-9]+
    - 中文双字及以上短语：[一-鿿]{2,}
    """
    return set(re.findall(r"[A-Za-z0-9]+|[一-鿿]{2,}", text.lower()))


def retrieve_chunks(query: str, top_k: int | None = None) -> list[dict[str, str]]:
    """基于词汇重叠度对文档片段评分，返回最相关的结果。

    算法：计算查询 tokens 和片段 tokens 的交集大小作为相关性分数，
    按分数降序返回 top_k 个结果。

    这是一个简易的关键词检索实现，生产环境建议替换为向量检索。
    """
    limit = top_k or settings.top_k_chunks
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    with get_db_session() as db:
        rows = db.execute(
            select(Document.filename, DocumentChunk.content)
            .join(Document, Document.id == DocumentChunk.document_id)
        ).all()

    # 计算每个片段与查询的词汇重叠分数
    scored: list[tuple[int, dict[str, str]]] = []
    for filename, content in rows:
        score = len(query_tokens & _tokens(content))
        if score > 0:
            scored.append((score, {"source": filename, "snippet": content[:300]}))

    # 按相关性分数降序排列，取前 top_k 个
    scored.sort(key=lambda item: item[0], reverse=True)
    return [item for _, item in scored[:limit]]


# ============================================================
# 评测（Eval）相关
# ============================================================


def create_eval_run(name: str, total: int, passed: int) -> int:
    """创建一次评测批次记录。"""
    with get_db_session() as db:
        run = EvalRun(name=name, total=total, passed=passed)
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id


def add_eval_result(
    eval_run_id: int,
    question: str,
    expected_tool: str,
    actual_tools: list[str],
    passed: bool,
    notes: str = "",
) -> None:
    """添加一条评测明细结果。"""
    with get_db_session() as db:
        db.add(
            EvalResult(
                eval_run_id=eval_run_id,
                question=question,
                expected_tool=expected_tool,
                actual_tools=",".join(actual_tools),
                passed=passed,
                notes=notes,
            )
        )
        db.commit()
