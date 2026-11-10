from __future__ import annotations

from typing import Any

from tools._shared import err

ALIGNMENT_MAP = {
    "left": ":---",
    "center": ":---:",
    "right": "---:",
}


def format_table(
    headers: list[str] = [],
    rows: list[list[Any]] = [],
    alignment: str = "left",
) -> dict[str, Any]:
    """Formats structured tabular data into an aligned Markdown table string."""
    if not isinstance(headers, list) or len(headers) == 0:
        return {
            "tool": "table_format",
            "error": "ValueError",
            "message": "headers must be a non-empty list of column names",
        }
    if not isinstance(rows, list):
        return {
            "tool": "table_format",
            "error": "TypeError",
            "message": "rows must be a list of row lists",
        }
    if alignment not in ALIGNMENT_MAP:
        return {
            "tool": "table_format",
            "error": "ValueError",
            "message": f"alignment must be one of {list(ALIGNMENT_MAP.keys())}",
        }

    try:
        clean_headers = [str(h).strip() for h in headers]
        num_cols = len(clean_headers)
        align_token = ALIGNMENT_MAP[alignment]
        sep_row = [align_token] * num_cols

        table_lines = [
            f"| {' | '.join(clean_headers)} |",
            f"| {' | '.join(sep_row)} |",
        ]

        clean_rows = []
        for r in rows:
            if not isinstance(r, (list, tuple)):
                row_items = [str(r)] + [""] * (num_cols - 1)
            else:
                row_items = [str(cell) for cell in r]
                if len(row_items) < num_cols:
                    row_items.extend([""] * (num_cols - len(row_items)))
                elif len(row_items) > num_cols:
                    row_items = row_items[:num_cols]
            clean_rows.append(row_items)
            table_lines.append(f"| {' | '.join(row_items)} |")

        markdown_output = "\n".join(table_lines)
        return {
            "tool": "table_format",
            "markdown_table": markdown_output,
            "rows_count": len(clean_rows),
            "cols_count": num_cols,
        }
    except Exception as exc:
        return err("table_format", exc)
