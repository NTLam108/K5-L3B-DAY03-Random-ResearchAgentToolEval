"""Web UI server for the Research Agent (Three.js front end in ./web).

Run from starter_v0/:
    python web_server.py --provider openrouter --version v3
then open http://127.0.0.1:8000

It reuses chat.py's tool loop and transcript writer, so every web conversation is saved
to transcripts/*.transcript.json in the same format as `chat.py`.
Standard library only (no extra dependency).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import threading
import time
import uuid
from collections import deque
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import chat
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
ARTIFACTS_DIR = ROOT / "artifacts"

MAX_BODY_BYTES = 16 * 1024
MAX_MESSAGE_CHARS = 2000
MAX_RESULT_CHARS = 6000
MAX_SESSIONS = 200
SESSION_ID_RE = re.compile(r"^[a-f0-9]{32}$")

# Tools shipped with the starter; anything else is shown as a team tool in the UI.
STARTER_TOOLS = {
    "clarify", "timeline", "social_search", "lookup", "fetch",
    "format", "send", "policy", "papers", "paper_text",
}
SECRET_ENV_VARS = [
    "OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
    "TAVILY_API_KEY", "FIRECRAWL_API_KEY", "RAPIDAPI_KEY", "TELEGRAM_BOT_TOKEN",
]


def redact(text: str) -> str:
    """Never let a configured secret leave the server, even inside a tool result or error."""
    for name in SECRET_ENV_VARS:
        value = os.getenv(name)
        if value and len(value) >= 8:
            text = text.replace(value, "***")
    return text


def shrink_result(result: Any) -> Any:
    text = json.dumps(result, ensure_ascii=False, default=str)
    if len(text) <= MAX_RESULT_CHARS:
        return result
    return {"_truncated": True, "preview": text[:MAX_RESULT_CHARS]}


def first_sentence(text: str, limit: int = 160) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


class Session:
    def __init__(self, session_id: str, transcript: dict[str, Any], path: Path) -> None:
        self.session_id = session_id
        self.history: list[dict[str, str]] = []
        self.transcript = transcript
        self.path = path
        self.lock = threading.Lock()
        self.turn_index = 0
        self.last_used = time.time()


class RateLimiter:
    """Global sliding window, so a public tunnel cannot burn the team's API quota."""

    def __init__(self, max_per_minute: int) -> None:
        self.max_per_minute = max_per_minute
        self.stamps: deque[float] = deque()
        self.lock = threading.Lock()

    def allow(self) -> bool:
        now = time.monotonic()
        with self.lock:
            while self.stamps and now - self.stamps[0] > 60:
                self.stamps.popleft()
            if len(self.stamps) >= self.max_per_minute:
                return False
            self.stamps.append(now)
            return True


class WebApp:
    def __init__(self, args: argparse.Namespace, provider: Any | None = None) -> None:
        self.args = args
        self.system_prompt = args.system_prompt.read_text(encoding="utf-8")
        self.declarations = load_tool_declarations(args.tools)
        self.openai_tools = to_openai_tools(self.declarations)
        self.provider = provider or make_provider(args.provider)
        self.model = args.model or getattr(self.provider, "default_model", None)
        self.artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)
        self.sessions: dict[str, Session] = {}
        self.sessions_lock = threading.Lock()
        self.limiter = RateLimiter(args.max_per_minute)
        self.index_html = (WEB_DIR / "index.html").read_bytes()
        self.csp = self._build_csp(self.index_html.decode("utf-8"))

    @staticmethod
    def _build_csp(html: str) -> str:
        match = re.search(r'<script type="importmap">(.*?)</script>', html, re.S)
        importmap_hash = ""
        if match:
            digest = base64.b64encode(hashlib.sha256(match.group(1).encode("utf-8")).digest()).decode()
            importmap_hash = f" 'sha256-{digest}'"
        return (
            "default-src 'none'; "
            f"script-src 'self' https://cdn.jsdelivr.net{importmap_hash}; "
            "style-src 'self'; img-src 'self' data:; connect-src 'self'; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
        )

    # ---- API ---------------------------------------------------------------

    def info(self) -> dict[str, Any]:
        key_env = getattr(self.provider, "api_key_env", None)
        return {
            "version": self.args.version,
            "artifact_version": self.artifact_version.artifact_version,
            "provider": self.args.provider,
            "model": self.model,
            "key_configured": bool(key_env and os.getenv(key_env)) if key_env else None,
            "tools": [
                {
                    "name": item["name"],
                    "description": first_sentence(item.get("description", "")),
                    "team_tool": item["name"] not in STARTER_TOOLS,
                }
                for item in self.declarations
            ],
        }

    def _new_session(self) -> Session:
        session_id = uuid.uuid4().hex
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([
            chat.safe_slug(self.args.version), "web", chat.safe_slug(self.args.provider), timestamp,
        ])
        path = self.args.transcripts_dir / f"{transcript_id}.transcript.json"
        transcript = {
            "transcript_id": transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": self.args.provider,
            "model": self.model,
            "system_prompt": str(self.args.system_prompt),
            "tools": str(self.args.tools),
            "history_window": self.args.history_window,
            "max_tool_rounds": self.args.max_tool_rounds,
            "client": "web",
            "created_at": chat.now_iso(),
            "updated_at": chat.now_iso(),
            "turns": [],
        }
        session = Session(session_id, transcript, path)
        with self.sessions_lock:
            if len(self.sessions) >= MAX_SESSIONS:
                oldest = min(self.sessions.values(), key=lambda s: s.last_used)
                self.sessions.pop(oldest.session_id, None)
            self.sessions[session_id] = session
        return session

    def _get_session(self, session_id: Any) -> Session:
        if isinstance(session_id, str) and SESSION_ID_RE.match(session_id):
            with self.sessions_lock:
                session = self.sessions.get(session_id)
            if session:
                return session
        return self._new_session()

    def reset(self, session_id: Any) -> None:
        if isinstance(session_id, str) and SESSION_ID_RE.match(session_id):
            with self.sessions_lock:
                self.sessions.pop(session_id, None)

    def chat(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        message = body.get("message")
        if not isinstance(message, str) or not message.strip():
            return 400, {"error": "message must be a non-empty string"}
        message = message.strip()
        if len(message) > MAX_MESSAGE_CHARS:
            return 400, {"error": f"message is longer than {MAX_MESSAGE_CHARS} characters"}
        if not self.limiter.allow():
            return 429, {"error": "Too many requests. Please wait a moment and try again."}

        session = self._get_session(body.get("session_id"))
        with session.lock:
            session.last_used = time.time()
            session.turn_index += 1
            messages = [
                {"role": "system", "content": self.system_prompt},
                *chat.trim_history(session.history, self.args.history_window),
                {"role": "user", "content": message},
            ]
            turn: dict[str, Any] = {
                "turn_index": session.turn_index,
                "started_at": chat.now_iso(),
                "user": message,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }
            status_code = 200
            try:
                result = chat.run_model_tool_loop(
                    provider=self.provider,
                    messages=messages,
                    tools=self.openai_tools,
                    model=self.args.model,
                    max_tool_rounds=self.args.max_tool_rounds,
                )
                turn.update(result)
                session.history.append({"role": "user", "content": message})
                session.history.append({"role": "assistant", "content": result["assistant_text"]})
                payload: dict[str, Any] = {
                    "session_id": session.session_id,
                    "status": result["status"],
                    "assistant_text": result["assistant_text"],
                    "tool_events": [
                        {"tool": e["tool"], "args": e["args"], "result": shrink_result(e["result"])}
                        for e in result["tool_events"]
                    ],
                }
            except Exception as exc:  # provider/network failure: keep it visible, never hide it
                message_text = redact(f"{type(exc).__name__}: {exc}")
                turn.update({"status": "provider_error", "error": message_text})
                payload = {"session_id": session.session_id, "status": "provider_error", "error": message_text}
                status_code = 502
            turn["ended_at"] = chat.now_iso()
            session.transcript["turns"].append(turn)
            chat.write_transcript(session.path, session.transcript)
        return status_code, payload


def make_handler(app: WebApp) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ResearchAgentWeb/1.0"

        def _headers(self, status: int, content_type: str, length: int) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", app.csp)
            self.end_headers()

        def _send_json(self, status: int, obj: Any) -> None:
            data = redact(json.dumps(obj, ensure_ascii=False, default=str)).encode("utf-8")
            self._headers(status, "application/json; charset=utf-8", len(data))
            self.wfile.write(data)

        def _send_bytes(self, status: int, content_type: str, data: bytes) -> None:
            self._headers(status, content_type, len(data))
            self.wfile.write(data)

        def _read_json(self) -> dict[str, Any] | None:
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = 0
            if length <= 0:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "empty body"})
                return None
            if length > MAX_BODY_BYTES:
                self._send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "body too large"})
                return None
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid JSON"})
                return None
            if not isinstance(body, dict):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "JSON object expected"})
                return None
            return body

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path in {"/", "/index.html"}:
                self._send_bytes(HTTPStatus.OK, "text/html; charset=utf-8", app.index_html)
            elif path == "/api/info":
                self._send_json(HTTPStatus.OK, app.info())
            elif path.startswith("/static/"):
                self._serve_static(path[len("/static/"):])
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def _serve_static(self, relative: str) -> None:
            target = (WEB_DIR / relative).resolve()
            if (
                not relative
                or "\\" in relative
                or not target.is_relative_to(WEB_DIR.resolve())
                or not target.is_file()
            ):
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if target.suffix == ".js":
                content_type = "text/javascript"
            if content_type.startswith("text/") or content_type.endswith("javascript"):
                content_type += "; charset=utf-8"
            self._send_bytes(HTTPStatus.OK, content_type, target.read_bytes())

        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path not in {"/api/chat", "/api/reset"}:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            body = self._read_json()
            if body is None:
                return
            if path == "/api/reset":
                app.reset(body.get("session_id"))
                self._send_json(HTTPStatus.OK, {"ok": True})
                return
            status, payload = app.chat(body)
            self._send_json(status, payload)

    return Handler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research Agent web UI (Three.js).")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini", "ollama"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Artifact version label, e.g. v3.")
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--host", default="127.0.0.1", help="Use 0.0.0.0 only if you really want LAN access.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--max-per-minute", type=int, default=20, help="Global chat requests per minute.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    app = WebApp(args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app))
    print(f"Research Agent web UI: http://{args.host}:{args.port}  (artifact_version={app.artifact_version.artifact_version})")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
