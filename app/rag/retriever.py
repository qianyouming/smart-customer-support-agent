"""RAG retriever facade."""

from app.db.crud import retrieve_chunks


def retrieve(query: str, top_k: int | None = None) -> list[dict[str, str]]:
    """Retrieve relevant chunks for a query from the database-backed store."""
    return retrieve_chunks(query=query, top_k=top_k)
