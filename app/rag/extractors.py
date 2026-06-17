"""上传文件的文本提取工具。

支持格式：.txt、.md、.csv、.json（直接 UTF-8 解码）和 .pdf（需要 pypdf 库）。
"""

from io import BytesIO
from pathlib import Path

# 可直接作为纯文本读取的文件扩展名
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json"}


def extract_upload_text(filename: str, content: bytes) -> str:
    """从上传文件中提取可读文本。

    Args:
        filename: 原始文件名（用于判断格式）
        content: 文件二进制内容

    Returns:
        提取并清洗后的文本

    Raises:
        ValueError: 不支持的文件格式，或文件内容为空
    """
    suffix = Path(filename).suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        # 纯文本类文件：直接 UTF-8 解码，忽略无法解码的字节
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
    """使用 pypdf 提取 PDF 文本内容。

    注意：扫描件 PDF 可能没有可提取的文本层，此时会返回空字符串。
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(page.strip() for page in pages if page.strip())
    except Exception as exc:
        raise ValueError("PDF text extraction failed. The file may be scanned or encrypted.") from exc
