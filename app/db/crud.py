"""Database CRUD helpers.

This module is the persistence boundary for sessions, messages, uploaded
documents, retrieval chunks, tool traces, and eval reports.
"""

import re
from collections.abc import Iterable
from datetime import datetime
from uuid import uuid4

from sqlalchemy import delete, func, select

from app.core.config import settings
from app.db.models import ChatSession, Document, DocumentChunk, EvalResult, EvalRun, Message, ToolCall
from app.db.session import get_db_session


def _is_test_session(session_id: str) -> bool:
    """Mark eval/test sessions so they do not clutter the user sidebar."""
    lowered = session_id.lower()
    return (
        lowered.startswith("test")
        or lowered.startswith("eval")
        or "test" in lowered
        or "eval" in lowered
    )


def _default_session_title(session_id: str) -> str:
    """Generate a friendly title before the first user message arrives."""
    if session_id.startswith("demo-"):
        return f"新会话 {datetime.now():%m-%d %H:%M}"
    return "新的客服咨询"


def _title_from_message(content: str) -> str:
    """Use the first user message as an automatic session title."""
    clean = " ".join(content.strip().split())
    if not clean:
        return "新的客服咨询"
    return clean[:28] + ("..." if len(clean) > 28 else "")


def _is_default_title(title: str | None) -> bool:
    """Only auto-rename sessions that still have a generated default title."""
    if not title:
        return True
    return title.startswith("新会话") or title == "新的客服咨询" or title == "客服会话"


def ensure_session(session_id: str) -> None:
    """Create a session row if it does not exist yet."""
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
    """Persist a message and update session title/timestamp when needed."""
    ensure_session(session_id)
    with get_db_session() as db:
        record = Message(session_id=session_id, role=role, content=content)
        db.add(record)
        session = db.get(ChatSession, session_id)
        if session is not None:
            session.updated_at = datetime.now()
        if role == "user":
            if session is not None and _is_default_title(session.title):
                session.title = _title_from_message(content)
        db.commit()
        db.refresh(record)
        return record.id


def get_recent_messages(session_id: str, limit: int | None = None) -> list[dict[str, str]]:
    """Load recent history for prompt context."""
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
    """Return sidebar summaries ordered by latest activity."""
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
    """Rename a session; returns False for empty titles."""
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
    """Delete a session and cascade-delete related messages/tool calls."""
    with get_db_session() as db:
        session = db.get(ChatSession, session_id)
        if session is None:
            return False
        db.delete(session)
        db.commit()
        return True


def list_session_messages(session_id: str) -> list[dict[str, str]]:
    """Return all messages for one session in chronological order."""
    ensure_session(session_id)
    with get_db_session() as db:
        rows = db.scalars(
            select(Message).where(Message.session_id == session_id).order_by(Message.id.asc())
        ).all()
    return [{"role": row.role, "content": row.content, "created_at": row.created_at.isoformat()} for row in rows]


def add_tool_call(session_id: str, tool_name: str, tool_input: str, tool_output: str) -> int:
    """Persist one tool invocation for traceability."""
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


def create_document(filename: str, chunks: Iterable[str], content_type: str = "text/plain") -> dict[str, str | int]:
    """Store a document and its chunks, replacing older uploads with same name."""
    document_id = str(uuid4())
    chunk_list = list(chunks)
    with get_db_session() as db:
        old_ids = db.scalars(select(Document.id).where(Document.filename == filename)).all()
        if old_ids:
            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id.in_(old_ids)))
            db.execute(delete(Document).where(Document.id.in_(old_ids)))
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
    """Delete a document and cascade-delete its chunks."""
    with get_db_session() as db:
        document = db.get(Document, document_id)
        if document is None:
            return False
        db.delete(document)
        db.commit()
        return True


def list_documents() -> list[dict[str, str | int]]:
    """Return document summaries for the knowledge-base sidebar."""
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
    """Return document metadata and all chunks for the detail page."""
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


def _tokens(text: str) -> set[str]:
    """Tokenize English words/numbers and short Chinese phrases for keyword search."""
    return set(re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", text.lower()))


def retrieve_chunks(query: str, top_k: int | None = None) -> list[dict[str, str]]:
    """Score chunks by token overlap and return the best matches."""
    limit = top_k or settings.top_k_chunks
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    with get_db_session() as db:
        rows = db.execute(
            select(Document.filename, DocumentChunk.content)
            .join(Document, Document.id == DocumentChunk.document_id)
        ).all()

    scored: list[tuple[int, dict[str, str]]] = []
    for filename, content in rows:
        score = len(query_tokens & _tokens(content))
        if score > 0:
            scored.append((score, {"source": filename, "snippet": content[:300]}))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item for _, item in scored[:limit]]


def create_eval_run(name: str, total: int, passed: int) -> int:
    """Create an eval run summary row."""
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
    """Append one detailed eval result row."""
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
