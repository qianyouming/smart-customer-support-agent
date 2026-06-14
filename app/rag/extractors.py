from io import BytesIO
from pathlib import Path

TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json"}


def extract_upload_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        text = content.decode("utf-8", errors="ignore")
    elif suffix == ".pdf":
        text = _extract_pdf_text(content)
    else:
        raise ValueError("Only .txt, .md, .csv, .json, and .pdf files are supported.")

    normalized = text.strip()
    if not normalized:
        raise ValueError("No extractable text was found in this file.")
    return normalized


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(page.strip() for page in pages if page.strip())
    except Exception as exc:
        raise ValueError("PDF text extraction failed. The file may be scanned or encrypted.") from exc
