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

## Resource limits (added after review)

The expression comes from the model (or a user prompting it), so evaluation is capped:

- Power (`**` and `pow(a, b)`): rejected when the estimated result exceeds about 10,000 bits
  (`10**10**10`, `9**9**9**9`, `pow(9, 99999999)` returned in minutes or never before this limit).
  `pow(a, b, m)` with a modulus is still allowed.
- Arithmetic on lists is rejected (`[0] * 10**9` would allocate gigabytes); lists are only accepted as arguments to `sum`, `min`, `max`.
- Expressions longer than 500 characters are rejected.
- Regression tests: `test_calc_rejects_huge_power_instead_of_hanging`, `test_calc_rejects_list_arithmetic_but_accepts_lists_as_arguments`, `test_calc_rejects_overlong_expression`.
