"""Compatibility wrapper around the database-backed document store.

Earlier versions used a JSON file store. These helpers keep the old boundary
available while routing reads through the SQL database.
"""

from typing import Any

from app.db.crud import list_documents as list_db_documents
from app.db.crud import retrieve_chunks


def load_store() -> dict[str, Any]:
    """Return a store-like snapshot for older code paths."""
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
    """No-op kept for compatibility after moving persistence into SQLite."""
    return None


def list_documents() -> list[dict[str, Any]]:
    """List document summaries from the database."""
    return list_db_documents()
