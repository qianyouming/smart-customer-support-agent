"""文档存储兼容层。

早期版本使用 JSON 文件存储，现已迁移至 SQL 数据库。
本模块保留旧接口供可能的遗留代码调用，实际数据读写走数据库。
"""

from typing import Any

from app.db.crud import list_documents as list_db_documents
from app.db.crud import retrieve_chunks


def load_store() -> dict[str, Any]:
    """返回类似旧 JSON 文件的存储快照，供兼容代码使用。"""
    documents = list_db_documents()
    chunks = [
        {
            "document_id": item["source"],
            "filename": item["source"],
            "text": item["snippet"],
        }
        for item in retrieve_chunks("", top_k=0)
    ]
    return {"documents": documents, "chunks": chunks}


def save_store(store: dict[str, Any]) -> None:
    """空操作：持久化已由 SQLite 数据库接管，保留接口仅为兼容性。"""
    return None


def list_documents() -> list[dict[str, Any]]:
    """列出所有文档摘要信息。"""
    return list_db_documents()
