---
name: calc
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [expression, precision]
outputs: [tool, expression, result, formatted]
side_effect: false
---
# calc

Safely evaluates mathematical and statistical expressions for research analysis (growth rates, averages, percentages, ratios) using an Abstract Syntax Tree (AST). Runs 100% locally with zero external network or API keys.

## Features & Capabilities

- Evaluates arithmetic operations: `+`, `-`, `*`, `/`, `//`, `**`, `%`.
- Supports safe math helpers: `round()`, `abs()`, `min()`, `max()`, `pow()`, `sum()`.
- Supports nested parentheses and floating point precision adjustments.
- Completely sandboxed: forbids arbitrary code execution, system imports, file access, and attribute lookups.
- Errors (such as syntax errors, division by zero, or unsupported operations) return a structured error dictionary (`{"tool": "calc", "error": ..., "message": ...}`) and never crash or raise unhandled exceptions.

## Usage Guidelines

- **When to use**: When the user or research workflow requires precise mathematical calculation, statistical ratios, metric changes, or percentages.
- **When NOT to use**: Do not use for natural language lookups, unit conversions requiring live currency exchange rates, or web searches.
