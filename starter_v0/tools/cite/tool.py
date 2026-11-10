from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from tools._shared import err

STYLES = ("apa", "bibtex")
MAX_AUTHORS = 20


def _surname_and_initials(name: str) -> tuple[str, str]:
    """Heuristic: the LAST word is the surname, earlier words become initials.

    Wrong for names written surname-first (e.g. many Vietnamese names) or surnames with
    several words; documented as a known limitation in TOOL.md.
    """
    parts = name.split()
    surname = parts[-1]
    initials = " ".join(f"{part[0].upper()}." for part in parts[:-1])
    return surname, initials


def _apa_author(name: str) -> str:
    surname, initials = _surname_and_initials(name)
    return f"{surname}, {initials}" if initials else surname


def _apa_author_list(names: list[str]) -> str:
    formatted = [_apa_author(name) for name in names]
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


def _year(published: str) -> str | None:
    head = (published or "").strip()[:4]
    return head if len(head) == 4 and head.isdigit() else None


def _validate(title: Any, authors: Any, published: Any, url: Any, style: Any) -> None:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")
    if not isinstance(authors, list) or not authors:
        raise TypeError("authors must be a non-empty list of names")
    if not all(isinstance(name, str) and name.strip() for name in authors):
        raise TypeError("every author must be a non-empty string")
    if len(authors) > MAX_AUTHORS:
        raise ValueError(f"too many authors ({len(authors)} > {MAX_AUTHORS})")
    if not isinstance(published, str) or not isinstance(url, str):
        raise TypeError("published and url must be strings")
    if style not in STYLES:
        raise ValueError(f"style must be one of {list(STYLES)}, got {style!r}")


def _apa(title: str, authors: list[str], published: str, url: str) -> str:
    year = _year(published) or "n.d."
    title = title.strip()
    if not title.endswith((".", "?", "!")):
        title += "."
    text = f"{_apa_author_list(authors)} ({year}). {title}"
    host = urlparse(url).netloc.replace("www.", "") if url else ""
    if host == "arxiv.org":
        text += " arXiv."
    if url:
        text += f" {url}"
    return text


def _bibtex(title: str, authors: list[str], published: str, url: str) -> str:
    year = _year(published)
    surname = re.sub(r"[^a-z0-9]", "", _surname_and_initials(authors[0].strip())[0].lower()) or "anon"
    key = f"{surname}{year or 'nd'}"
    fields = [f"  title = {{{title.strip()}}}", f"  author = {{{' and '.join(name.strip() for name in authors)}}}"]
    if year:
        fields.append(f"  year = {{{year}}}")
    if url:
        fields.append(f"  url = {{{url}}}")
    return f"@misc{{{key},\n" + ",\n".join(fields) + "\n}"


def make_citation(
    title: str = "",
    authors: list[str] | None = None,
    published: str = "",
    url: str = "",
    style: str = "apa",
) -> dict[str, Any]:
    try:
        _validate(title, authors, published, url, style)
        builder = _apa if style == "apa" else _bibtex
        return {"tool": "cite", "style": style, "citation": builder(title, authors, published, url)}
    except Exception as exc:
        return err("cite", exc)
