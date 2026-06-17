"""知识库文档相关的 Pydantic 数据模型。"""

from pydantic import BaseModel


class DocumentIngestResponse(BaseModel):
    """文件上传并分块后的响应。"""

    document_id: str            # 生成的文档唯一 ID
    filename: str               # 原始文件名
    chunks_created: int         # 成功创建的片段数


class DocumentSummary(BaseModel):
    """文档摘要：侧边栏中的轻量级展示。"""

    document_id: str
    filename: str
    chunks_count: int           # 该文档包含的片段总数


class DocumentChunkView(BaseModel):
    """单个文档片段：详情页中展示的分块内容。"""

    chunk_index: int            # 片段在文档中的顺序索引
    content: str                # 片段文本内容


class DocumentDetail(BaseModel):
    """文档完整详情：包含元数据和所有片段。"""

    document_id: str
    filename: str
    content_type: str
    chunks_count: int
    chunks: list[DocumentChunkView]
