"""Tool registry used by real LLM tool-calling paths."""

from collections.abc import Callable

from app.tools import calculator, retrieval, search

TOOLS = [calculator.TOOL_SCHEMA, search.TOOL_SCHEMA, retrieval.TOOL_SCHEMA]

TOOL_MAP: dict[str, Callable[..., str]] = {
    "calculator": calculator.run,
    "search": search.run,
    "retrieval": retrieval.run,
}


def get_tool_map() -> dict[str, Callable[..., str]]:
    """Return name-to-function mapping for executable tools."""
    return TOOL_MAP
