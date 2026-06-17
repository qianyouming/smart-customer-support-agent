"""文本分块工具，用于简易 RAG 管道。

将长文本切分为有重叠的小片段，确保检索时不会丢失跨片段边界的上下文。
"""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """将文本按固定大小切分为带重叠的片段。

    Args:
        text: 待分块的原始文本
        chunk_size: 每个片段的最大字符数（默认 500）
        overlap: 相邻片段的重叠字符数（默认 80），保留上下文连续性

    Returns:
        切分后的文本片段列表

    算法说明：
        使用滑动窗口方式，每次前进 (chunk_size - overlap) 个字符，
        使得相邻片段之间有 overlap 个字符的重复，避免在切分边界丢失语义。
    """
    # 合并多余空白为单个空格，规范化文本
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunks.append(normalized[start:end])
        # 滑动窗口前进，确保 overlap 生效且不会无限循环
        start = end if overlap <= 0 else max(end - overlap, start + 1)
    return chunks
