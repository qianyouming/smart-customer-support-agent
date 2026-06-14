"""Safe calculator tool.

The tool parses arithmetic with Python's AST instead of using eval(), so only
simple numeric expressions are accepted.
"""

import ast
import operator
import re
from typing import Callable

TOOL_SCHEMA = {
    "type": "function",
    "name": "calculator",
    "description": "Evaluate a safe arithmetic expression.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Arithmetic expression, e.g. 23 * 47"}
        },
        "required": ["expression"],
    },
}

_OPS: dict[type[ast.AST], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def _eval_node(node: ast.AST) -> float:
    """Recursively evaluate a whitelisted AST expression node."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_node(node.operand)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    raise ValueError("Only simple arithmetic expressions are allowed.")


def extract_expression(text: str) -> str | None:
    """Extract the first arithmetic-looking expression from user text."""
    match = re.search(r"[-+*/().\d\s]+", text)
    if not match:
        return None
    expression = match.group(0).strip()
    return expression if any(op in expression for op in "+-*/") else None


def run(expression: str) -> str:
    """Evaluate an arithmetic expression and return a display-friendly result."""
    tree = ast.parse(expression, mode="eval")
    result = _eval_node(tree)
    if result.is_integer():
        return str(int(result))
    return str(result)
