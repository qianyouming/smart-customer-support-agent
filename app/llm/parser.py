"""Small helper for parsing model output."""

import json
from typing import Any


def parse_json_or_text(raw: str) -> dict[str, Any]:
    """Return JSON objects when possible, otherwise wrap raw text as answer."""
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    return {"answer": raw}
