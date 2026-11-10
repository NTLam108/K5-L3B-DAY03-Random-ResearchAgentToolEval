---
name: table_format
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [headers, rows, alignment]
outputs: [tool, markdown_table, rows_count, cols_count]
side_effect: false
---
# table_format

Formats structured tabular data into clean, aligned GitHub-flavored Markdown tables. Runs 100% locally with zero external network or API keys.

## Features & Capabilities

- Accepts custom headers and arbitrary 2D data rows.
- Automatically handles row padding or truncation to ensure valid tabular alignment.
- Supports flexible column alignment syntax: `left` (`:---`), `center` (`:---:`), and `right` (`---:`).
- Gracefully handles type errors or malformed inputs by returning a structured error dictionary (`{"tool": "table_format", "error": ..., "message": ...}`) without raising exceptions.

## Usage Guidelines

- **When to use**: When presenting benchmark results, evaluation comparison matrices, model metric scorecards, or structured research data in Markdown.
- **When NOT to use**: Do not use for natural text summarization or single-column bullet points (use `format` instead).
