from __future__ import annotations

import ast
import operator
from typing import Any

from tools._shared import err

# Safe operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Safe built-in functions
ALLOWED_FUNCTIONS = {
    "round": round,
    "abs": abs,
    "min": min,
    "max": max,
    "pow": pow,
    "sum": sum,
}


def _eval_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError(f"Unsupported constant type: {type(node.value).__name__}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand)
        return OPERATORS[op_type](operand)
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple named function calls are permitted")
        fn_name = node.func.id
        if fn_name not in ALLOWED_FUNCTIONS:
            raise ValueError(f"Function '{fn_name}' is not permitted")
        args = [_eval_node(arg) for arg in node.args]
        return ALLOWED_FUNCTIONS[fn_name](*args)
    elif isinstance(node, ast.List):
        return [_eval_node(item) for item in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(_eval_node(item) for item in node.elts)
    raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")


def evaluate_math(expression: str = "", precision: int = 2) -> dict[str, Any]:
    """Safely evaluates a math or statistical formula without using unsafe eval()."""
    if not isinstance(expression, str) or not expression.strip():
        return {
            "tool": "calc",
            "error": "ValueError",
            "message": "expression must be a non-empty string",
        }
    try:
        parsed = ast.parse(expression.strip(), mode="eval")
        raw_result = _eval_node(parsed.body)
        if isinstance(raw_result, float):
            result = round(raw_result, precision)
        else:
            result = raw_result
        return {
            "tool": "calc",
            "expression": expression.strip(),
            "result": result,
            "formatted": str(result),
        }
    except Exception as exc:
        return err("calc", exc)
