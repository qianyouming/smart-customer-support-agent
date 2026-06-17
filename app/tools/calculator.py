"""安全计算器工具。

使用 Python AST 解析算术表达式（而非 eval()），只接受简单的数值运算，
防止代码注入风险。支持：加减乘除、幂运算、取模、负数。
"""

import ast
import operator
import re
from typing import Callable

# 工具 Schema 定义，供 LLM 工具调用协议使用
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

# 白名单运算符映射：AST 节点类型 → 对应的 Python 运算函数
_OPS: dict[type[ast.AST], Callable[[float, float], float]] = {
    ast.Add: operator.add,       # 加法
    ast.Sub: operator.sub,       # 减法
    ast.Mult: operator.mul,      # 乘法
    ast.Div: operator.truediv,   # 除法
    ast.Pow: operator.pow,       # 幂运算
    ast.Mod: operator.mod,       # 取模
}


def _eval_node(node: ast.AST) -> float:
    """递归求值白名单内的 AST 表达式节点。

    只允许常量数值、一元负号和二元算术运算，
    其他任何节点类型都会抛出 ValueError。
    """
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
    """从用户消息中提取第一个看起来像算术表达式的部分。

    匹配规则：连续的数字、运算符和括号序列，
    且至少包含一个运算符（+、-、*、/）才视为有效表达式。
    """
    match = re.search(r"[-+*/().\d\s]+", text)
    if not match:
        return None
    expression = match.group(0).strip()
    return expression if any(op in expression for op in "+-*/") else None


def run(expression: str) -> str:
    """计算算术表达式并返回用于展示的字符串结果。

    整数结果去掉小数点（如 6.0 → "6"），浮点数保留原样。
    """
    tree = ast.parse(expression, mode="eval")
    result = _eval_node(tree)
    if result.is_integer():
        return str(int(result))
    return str(result)
