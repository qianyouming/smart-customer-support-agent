"""Document ingestion entry point."""

from app.db.crud import create_document
from app.rag.chunking import chunk_text


def ingest_text(filename: str, text: str) -> dict[str, str | int]:
    """Chunk one document and persist it to the database."""
    chunks = chunk_text(text)
    return create_document(filename=filename, chunks=chunks)
