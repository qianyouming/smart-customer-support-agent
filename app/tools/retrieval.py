"""文档检索工具，从用户上传的文档片段中查找相关内容。"""

from app.rag.retriever import retrieve

# 工具 Schema 定义
TOOL_SCHEMA = {
    "type": "function",
    "name": "retrieval",
    "description": "Retrieve relevant chunks from uploaded documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Retrieval query"}
        },
        "required": ["query"],
    },
}


def run(query: str) -> str:
    """检索相关文档片段并格式化为带引用的文本。

    返回格式：'[文件名] 片段内容'，每行一条结果。
    前端和 runner 会解析此格式提取结构化引用。
    """
    chunks = retrieve(query)
    if not chunks:
        return "没有检索到相关文档片段。"
    return "\n\n".join(f"[{item['source']}] {item['snippet']}" for item in chunks)
