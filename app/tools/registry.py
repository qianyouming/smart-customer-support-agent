"""工具注册表，供真实 LLM 工具调用路径使用。

集中管理所有可用工具的 Schema 定义和执行函数映射，
便于 LLM function calling 时动态发现和调用工具。
"""

from collections.abc import Callable

from app.tools import calculator, retrieval, search

# 所有工具的 JSON Schema 列表，传递给 LLM 的 tools 参数
TOOLS = [calculator.TOOL_SCHEMA, search.TOOL_SCHEMA, retrieval.TOOL_SCHEMA]

# 工具名称 → 执行函数的映射表
TOOL_MAP: dict[str, Callable[..., str]] = {
    "calculator": calculator.run,
    "search": search.run,
    "retrieval": retrieval.run,
}


def get_tool_map() -> dict[str, Callable[..., str]]:
    """返回工具名称到执行函数的映射，供调度器按名称调用。"""
    return TOOL_MAP
