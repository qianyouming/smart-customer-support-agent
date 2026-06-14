from app.rag.retriever import retrieve

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
    chunks = retrieve(query)
    if not chunks:
        return "没有检索到相关文档片段。"
    return "\n\n".join(f"[{item['source']}] {item['snippet']}" for item in chunks)

