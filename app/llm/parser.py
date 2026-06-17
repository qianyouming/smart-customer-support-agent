"""LLM 输出解析工具。"""

import json
from typing import Any


def parse_json_or_text(raw: str) -> dict[str, Any]:
    """尝试将模型原始输出解析为 JSON，失败则包装为纯文本回答。

    某些模型可能返回结构化 JSON，也可能返回纯文本。
    本函数统一处理两种情况，确保下游始终得到字典格式。
    """
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    return {"answer": raw}
