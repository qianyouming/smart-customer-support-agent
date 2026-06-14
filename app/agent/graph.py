"""Conceptual Agent graph description.

The current implementation is intentionally lightweight and rule-based. This
file documents the intended workflow for a future LangGraph-style refactor.
"""

from typing import TypedDict


class AgentGraphState(TypedDict, total=False):
    """Possible state fields if the workflow is moved into a graph."""

    question: str
    rewritten_question: str
    retrieved_context: str
    answer: str


def describe_graph() -> list[str]:
    """Return the high-level workflow steps in execution order."""
    return [
        "rewrite_query",
        "retrieve_docs",
        "decide_tool",
        "generate_answer",
        "attach_citations",
    ]
