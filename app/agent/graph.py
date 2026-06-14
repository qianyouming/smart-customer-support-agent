from typing import TypedDict


class AgentGraphState(TypedDict, total=False):
    question: str
    rewritten_question: str
    retrieved_context: str
    answer: str


def describe_graph() -> list[str]:
    return [
        "rewrite_query",
        "retrieve_docs",
        "decide_tool",
        "generate_answer",
        "attach_citations",
    ]

