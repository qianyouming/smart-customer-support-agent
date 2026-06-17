"""RAG 检索器外观层。

为上层提供统一的检索接口，底层实现委托给数据库 CRUD 层。
未来可在此层插入向量检索、混合检索等更复杂的策略。
"""

from app.db.crud import retrieve_chunks


def retrieve(query: str, top_k: int | None = None) -> list[dict[str, str]]:
    """根据查询从数据库中检索最相关的文档片段。

    Args:
        query: 用户查询文本
        top_k: 返回的最大片段数（None 时使用全局配置的 top_k_chunks）

    Returns:
        包含 source（文件名）和 snippet（片段内容）的字典列表
    """
    return retrieve_chunks(query=query, top_k=top_k)
