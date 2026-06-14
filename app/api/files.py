from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db.crud import delete_document, get_document_detail
from app.rag.ingest import ingest_text
from app.rag.extractors import extract_upload_text
from app.rag.store import list_documents
from app.schemas.file import DocumentDetail, DocumentIngestResponse, DocumentSummary

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("", response_model=DocumentIngestResponse)
async def upload_file(file: UploadFile = File(...)) -> DocumentIngestResponse:
    content = await file.read()
    try:
        text = extract_upload_text(filename=file.filename or "uploaded.txt", content=content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = ingest_text(filename=file.filename or "uploaded.txt", text=text)
    return DocumentIngestResponse(**result)


@router.get("", response_model=list[DocumentSummary])
def get_files() -> list[DocumentSummary]:
    return [DocumentSummary(**item) for item in list_documents()]


@router.get("/{document_id}", response_model=DocumentDetail)
def get_file_detail(document_id: str) -> DocumentDetail:
    document = get_document_detail(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentDetail(**document)


@router.delete("/{document_id}")
def remove_file(document_id: str) -> dict[str, bool]:
    deleted = delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"deleted": True}
