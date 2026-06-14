from typing import Any

from app.db.crud import list_documents as list_db_documents
from app.db.crud import retrieve_chunks


def load_store() -> dict[str, Any]:
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
    return None


def list_documents() -> list[dict[str, Any]]:
    return list_db_documents()
