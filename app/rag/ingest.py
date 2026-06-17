"""文档入库入口模块。

负责将原始文本分块后持久化到数据库，完成从"上传"到"可检索"的转换。
"""

from app.db.crud import create_document
from app.rag.chunking import chunk_text


def ingest_text(filename: str, text: str) -> dict[str, str | int]:
    """将一份文档分块并存入数据库。

    Args:
        filename: 文件名（用于后续检索时标注来源）
        text: 提取好的纯文本内容

    Returns:
        包含 document_id、filename、chunks_created 的结果字典
    """
    chunks = chunk_text(text)
    return create_document(filename=filename, chunks=chunks)
