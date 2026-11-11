"""Vercel entry point for the Research Agent web UI.

Vercel's Python runtime serves a WSGI/ASGI callable named `app`. web_server.py is built
on http.server, so this file exposes a small WSGI adapter that replays each request
through the exact same BaseHTTPRequestHandler (same routes, security headers, rate limit).
web_server.py itself is unchanged.

Vercel can only write to /tmp, so transcripts and arXiv PDFs go there. They are
temporary on Vercel: the transcripts used as evidence come from local runs.
"""
from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qsl, urlencode

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.paper_text.tool as paper_text_tool  # noqa: E402
from web_server import WebApp, build_parser, make_handler  # noqa: E402

paper_text_tool.ARXIV_DIR = Path("/tmp/arxiv_papers")

args = build_parser().parse_args([
    "--provider", os.getenv("UI_PROVIDER", "openrouter"),
    "--version", os.getenv("UI_VERSION", "v3-14tools"),
    "--transcripts-dir", "/tmp/transcripts",
    "--max-per-minute", os.getenv("UI_MAX_PER_MINUTE", "10"),
])
_Handler = make_handler(WebApp(args))

# WSGI forbids hop-by-hop headers in the response.
_HOP_BY_HOP = {"connection", "keep-alive", "transfer-encoding", "upgrade",
               "proxy-authenticate", "proxy-authorization", "te", "trailers"}


def _original_target(environ: dict) -> str:
    """vercel.json rewrites every path to /api/index?__path=/<original>; undo that here."""
    path = environ.get("PATH_INFO") or "/"
    params = parse_qsl(environ.get("QUERY_STRING") or "", keep_blank_values=True)
    rest = []
    for key, value in params:
        if key == "__path":
            path = value or "/"
        else:
            rest.append((key, value))
    if not path.startswith("/"):
        path = "/" + path
    return path + (f"?{urlencode(rest)}" if rest else "")


def _raw_request(environ: dict) -> bytes:
    target = _original_target(environ)
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""

    headers = []
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            headers.append(f"{key[5:].replace('_', '-').title()}: {value}")
    if environ.get("CONTENT_TYPE"):
        headers.append(f"Content-Type: {environ['CONTENT_TYPE']}")
    headers.append(f"Content-Length: {len(body)}")

    head = f"{environ.get('REQUEST_METHOD', 'GET')} {target} HTTP/1.1\r\n" + "\r\n".join(headers) + "\r\n\r\n"
    return head.encode("latin-1", errors="replace") + body


def app(environ, start_response):
    handler = _Handler.__new__(_Handler)  # skip socket setup; drive it with in-memory streams
    handler.rfile = BytesIO(_raw_request(environ))
    handler.wfile = BytesIO()
    handler.client_address = (environ.get("REMOTE_ADDR", "0.0.0.0"), 0)
    handler.server = None
    handler.request = None
    handler.close_connection = True
    handler.handle_one_request()

    raw = handler.wfile.getvalue()
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")
    status = lines[0].split(" ", 1)[1] if lines and " " in lines[0] else "500 Internal Server Error"
    response_headers = []
    for line in lines[1:]:
        name, sep, value = line.partition(":")
        if sep and name.strip().lower() not in _HOP_BY_HOP:
            response_headers.append((name.strip(), value.strip()))
    start_response(status, response_headers)
    return [body]
