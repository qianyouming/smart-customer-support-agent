"""Pydantic schemas for knowledge-base document APIs."""

from pydantic import BaseModel


class DocumentIngestResponse(BaseModel):
    """Response returned after a file is uploaded and chunked."""

    document_id: str
    filename: str
    chunks_created: int


class DocumentSummary(BaseModel):
    """Lightweight document row for the sidebar."""

    document_id: str
    filename: str
    chunks_count: int


class DocumentChunkView(BaseModel):
    """One parsed chunk displayed on the document detail page."""

    chunk_index: int
    content: str


class DocumentDetail(BaseModel):
    """Full document detail with all chunks."""

    document_id: str
    filename: str
    content_type: str
    chunks_count: int
    chunks: list[DocumentChunkView]
