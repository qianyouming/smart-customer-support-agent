"""Text chunking utilities for the simple RAG pipeline."""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks so retrieval keeps nearby context."""
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunks.append(normalized[start:end])
        start = end if overlap <= 0 else max(end - overlap, start + 1)
    return chunks
