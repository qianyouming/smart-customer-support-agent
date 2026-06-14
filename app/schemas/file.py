from pydantic import BaseModel


class DocumentIngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    chunks_count: int


class DocumentChunkView(BaseModel):
    chunk_index: int
    content: str


class DocumentDetail(BaseModel):
    document_id: str
    filename: str
    content_type: str
    chunks_count: int
    chunks: list[DocumentChunkView]
