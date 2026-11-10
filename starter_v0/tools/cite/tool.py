from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from tools._shared import err

STYLES = ("apa", "bibtex")
APA_MAX_LISTED = 20  # APA 7: with 21+ authors list the first 19, an ellipsis, then the last author.


def _split_name(name: str) -> tuple[str, list[str]]:
    """Heuristic: the LAST word is the surname, earlier words are given names.

    Wrong for names written surname-first (e.g. many Vietnamese names) and multi-word surnames;
    documented as a known limitation in TOOL.md.
    """
    parts = name.split()
    return parts[-1], parts[:-1]


def _apa_author(name: str) -> str:
    surname, given = _split_name(name)
    initials = " ".join(f"{part[0].upper()}." for part in given)
    return f"{surname}, {initials}" if initials else surname


def _apa_author_list(names: list[str]) -> str:
    formatted = [_apa_author(name) for name in names]
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) > APA_MAX_LISTED:
        return ", ".join(formatted[:19]) + ", ... " + formatted[-1]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


def _year(published: str) -> str | None:
    head = (published or "").strip()[:4]
    return head if len(head) == 4 and head.isdigit() else None


def _validate(title: Any, authors: Any, published: Any, url: Any, style: Any) -> list[str]:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")
    if authors is None:
        authors = []
    if not isinstance(authors, list):
        raise TypeError("authors must be a list of names (empty list = no author)")
    if not all(isinstance(name, str) and name.strip() for name in authors):
        raise TypeError("every author must be a non-empty string")
    if not isinstance(published, str) or not isinstance(url, str):
        raise TypeError("published and url must be strings")
    if style not in STYLES:
        raise ValueError(f"style must be one of {list(STYLES)}, got {style!r}")
    return [name.strip() for name in authors]


def _with_period(text: str) -> str:
    return text if text.endswith((".", "?", "!")) else text + "."


def _apa(title: str, authors: list[str], published: str, url: str) -> str:
    year = _year(published) or "n.d."
    title = _with_period(title.strip())
    if authors:
        text = f"{_apa_author_list(authors)} ({year}). {title}"
    else:
        # APA: no author -> the title moves to the author position.
        text = f"{title} ({year})."
    host = urlparse(url).netloc.replace("www.", "") if url else ""
    if host == "arxiv.org":
        text += " arXiv."
    if url:
        text += f" {url}"
    return text


def _bibtex_author(name: str) -> str:
    surname, given = _split_name(name)
    return f"{surname}, {' '.join(given)}" if given else surname


def _bibtex(title: str, authors: list[str], published: str, url: str) -> str:
    year = _year(published)
    first_surname = _split_name(authors[0])[0] if authors else "anon"
    key_base = re.sub(r"[^a-z0-9]", "", first_surname.lower()) or "anon"
    fields = [f"  title = {{{title.strip()}}}"]
    if authors:
        fields.append(f"  author = {{{' and '.join(_bibtex_author(name) for name in authors)}}}")
    if year:
        fields.append(f"  year = {{{year}}}")
    if url:
        fields.append(f"  url = {{{url}}}")
    return f"@misc{{{key_base}{year or 'nd'},\n" + ",\n".join(fields) + "\n}"


def make_citation(
    title: str = "",
    authors: list[str] | None = None,
    published: str = "",
    url: str = "",
    style: str = "apa",
) -> dict[str, Any]:
    try:
        clean_authors = _validate(title, authors, published, url, style)
        builder = _apa if style == "apa" else _bibtex
        return {"tool": "cite", "style": style, "citation": builder(title, clean_authors, published, url)}
    except Exception as exc:
        return err("cite", exc)
