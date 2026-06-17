"""知识库文件管理 API 路由。

上传的文件经过文本提取、分块后存入数据库，
供 RAG 检索工具在对话中使用。
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db.crud import delete_document, get_document_detail
from app.rag.ingest import ingest_text
from app.rag.extractors import extract_upload_text
from app.rag.store import list_documents
from app.schemas.file import DocumentDetail, DocumentIngestResponse, DocumentSummary

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("", response_model=DocumentIngestResponse)
async def upload_file(file: UploadFile = File(...)) -> DocumentIngestResponse:
    """上传文件并持久化其提取的文本片段。

    处理流程：读取文件 → 提取文本 → 分块 → 存入数据库
    支持格式：.txt, .md, .csv, .json, .pdf
    """
    content = await file.read()
    try:
        text = extract_upload_text(filename=file.filename or "uploaded.txt", content=content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = ingest_text(filename=file.filename or "uploaded.txt", text=text)
    return DocumentIngestResponse(**result)


@router.get("", response_model=list[DocumentSummary])
def get_files() -> list[DocumentSummary]:
    """列出所有已上传的文档（不包含片段内容）。"""
    return [DocumentSummary(**item) for item in list_documents()]


@router.get("/{document_id}", response_model=DocumentDetail)
def get_file_detail(document_id: str) -> DocumentDetail:
    """返回单个文档的元数据和所有片段内容，供详情页展示。"""
    document = get_document_detail(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentDetail(**document)


@router.delete("/{document_id}")
def remove_file(document_id: str) -> dict[str, bool]:
    """删除文档及其关联的所有片段。"""
    deleted = delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"deleted": True}
