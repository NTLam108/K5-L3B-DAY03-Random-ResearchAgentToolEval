"""Offline tests for web_server.py: fake provider, real HTTP server on an ephemeral port.

http.client is used (not requests) because conftest blocks requests.Session for real network.
"""
from __future__ import annotations

import argparse
import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import web_server
from providers.base import ModelResponse, ToolCall

ROOT = Path(__file__).resolve().parents[1]


class ScriptedProvider:
    """Returns the queued responses in order; records nothing else."""

    api_key_env = "OPENROUTER_API_KEY"
    default_model = "fake-model"

    def __init__(self, responses: list[ModelResponse]) -> None:
        self.responses = list(responses)

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None) -> ModelResponse:
        if not self.responses:
            raise RuntimeError("provider exploded")
        return self.responses.pop(0)


def make_args(tmp_path: Path, **overrides) -> argparse.Namespace:
    values = dict(
        provider="openrouter", model=None, version="vtest",
        system_prompt=ROOT / "artifacts" / "system_prompt.md",
        tools=ROOT / "artifacts" / "tools.yaml",
        transcripts_dir=tmp_path, history_window=5, max_tool_rounds=4,
        host="127.0.0.1", port=0, max_per_minute=20,
    )
    values.update(overrides)
    return argparse.Namespace(**values)


@pytest.fixture
def serve(tmp_path):
    servers: list[ThreadingHTTPServer] = []

    def _start(responses: list[ModelResponse], **overrides):
        app = web_server.WebApp(make_args(tmp_path, **overrides), provider=ScriptedProvider(responses))
        server = ThreadingHTTPServer(("127.0.0.1", 0), web_server.make_handler(app))
        threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
        servers.append(server)
        return server.server_address[1], app

    yield _start
    for server in servers:
        server.shutdown()
        server.server_close()


def request(port: int, method: str, path: str, body: dict | bytes | None = None, headers: dict | None = None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    raw = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    send_headers = {"Content-Type": "application/json", **(headers or {})}
    conn.request(method, path, body=raw, headers=send_headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return response.status, response, data


def test_info_lists_tools_and_marks_team_tool(serve) -> None:
    port, _ = serve([])
    status, _, data = request(port, "GET", "/api/info")
    info = json.loads(data)
    tools = {tool["name"]: tool for tool in info["tools"]}
    assert status == 200
    assert info["version"] == "vtest"
    assert "cite" in tools and tools["cite"]["team_tool"] is True
    assert tools["lookup"]["team_tool"] is False


def test_index_page_is_served_with_security_headers(serve) -> None:
    port, _ = serve([])
    status, response, data = request(port, "GET", "/")
    assert status == 200
    assert b"importmap" in data
    csp = response.getheader("Content-Security-Policy")
    assert "sha256-" in csp and "frame-ancestors 'none'" in csp
    assert response.getheader("X-Content-Type-Options") == "nosniff"


def test_static_path_traversal_is_rejected(serve) -> None:
    port, _ = serve([])
    for path in ["/static/../web_server.py", "/static/..%2fweb_server.py", "/static/%2e%2e/.env", "/static/"]:
        status, _, data = request(port, "GET", path)
        assert status == 404, path
        assert b"import" not in data


def test_static_assets_have_javascript_content_type(serve) -> None:
    port, _ = serve([])
    status, response, _ = request(port, "GET", "/static/app.js")
    assert status == 200
    assert response.getheader("Content-Type").startswith("text/javascript")


def test_chat_runs_cite_tool_and_saves_transcript(serve, tmp_path) -> None:
    call = ToolCall("cite", {"title": "Attention Is All You Need", "authors": ["Ashish Vaswani"], "published": "2017"})
    port, _ = serve([
        ModelResponse(text=None, tool_calls=[call]),
        ModelResponse(text="Đây là citation của bạn.", tool_calls=[]),
    ])
    status, _, data = request(port, "POST", "/api/chat", {"message": "citation APA giúp mình"})
    payload = json.loads(data)

    assert status == 200
    assert payload["status"] == "answered"
    assert payload["assistant_text"] == "Đây là citation của bạn."
    event = payload["tool_events"][0]
    assert event["tool"] == "cite"
    assert event["result"]["citation"] == "Vaswani, A. (2017). Attention Is All You Need."

    saved = list(tmp_path.glob("*.transcript.json"))
    assert len(saved) == 1
    transcript = json.loads(saved[0].read_text(encoding="utf-8"))
    assert transcript["client"] == "web"
    assert transcript["turns"][0]["user"] == "citation APA giúp mình"
    assert transcript["turns"][0]["tool_events"][0]["tool"] == "cite"


def test_chat_keeps_history_within_the_same_session(serve) -> None:
    port, app = serve([
        ModelResponse(text="Bạn muốn xem tài khoản nào?", tool_calls=[]),
        ModelResponse(text="Ok.", tool_calls=[]),
    ])
    first = json.loads(request(port, "POST", "/api/chat", {"message": "tóm tắt tweet"})[2])
    second = json.loads(request(port, "POST", "/api/chat", {"message": "của Elon", "session_id": first["session_id"]})[2])
    assert second["session_id"] == first["session_id"]
    assert len(app.sessions[first["session_id"]].history) == 4


def test_clarify_tool_reports_waiting_for_user(serve) -> None:
    call = ToolCall("clarify", {"question": "Bạn muốn xem tài khoản nào?", "response_type": "text"})
    port, _ = serve([ModelResponse(text=None, tool_calls=[call])])
    payload = json.loads(request(port, "POST", "/api/chat", {"message": "tóm tắt tweet"})[2])
    assert payload["status"] == "waiting_for_user"
    assert payload["assistant_text"] == "Bạn muốn xem tài khoản nào?"


@pytest.mark.parametrize("body", [{}, {"message": ""}, {"message": "   "}, {"message": 123}, {"message": "x" * 2001}])
def test_chat_rejects_invalid_message(serve, body) -> None:
    port, _ = serve([])
    status, _, data = request(port, "POST", "/api/chat", body)
    assert status == 400
    assert "error" in json.loads(data)


def test_chat_rejects_bad_json_and_oversize_body(serve) -> None:
    port, _ = serve([])
    assert request(port, "POST", "/api/chat", b"{not json")[0] == 400
    assert request(port, "POST", "/api/chat", b"[1, 2]")[0] == 400
    assert request(port, "POST", "/api/chat", b"{" + b" " * (web_server.MAX_BODY_BYTES + 10) + b"}")[0] == 413


def test_rate_limit_returns_429_after_the_limit(serve) -> None:
    port, _ = serve([ModelResponse(text="ok", tool_calls=[]) for _ in range(3)], max_per_minute=2)
    statuses = [request(port, "POST", "/api/chat", {"message": f"hi {i}"})[0] for i in range(3)]
    assert statuses == [200, 200, 429]


def test_provider_failure_is_visible_and_secret_is_redacted(serve, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-secret-123456")

    class Leaky:
        api_key_env = "OPENROUTER_API_KEY"
        default_model = "fake"

        def complete(self, *args, **kwargs):
            raise RuntimeError("401 bad key sk-test-secret-123456")

    app = web_server.WebApp(make_args(tmp_path), provider=Leaky())
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_server.make_handler(app))
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    try:
        status, _, data = request(server.server_address[1], "POST", "/api/chat", {"message": "hi"})
    finally:
        server.shutdown()
        server.server_close()
    assert status == 502
    assert b"sk-test-secret-123456" not in data
    assert b"RuntimeError" in data and b"***" in data


def test_reset_drops_the_session(serve) -> None:
    port, app = serve([ModelResponse(text="ok", tool_calls=[])])
    session_id = json.loads(request(port, "POST", "/api/chat", {"message": "hi"})[2])["session_id"]
    assert session_id in app.sessions
    assert request(port, "POST", "/api/reset", {"session_id": session_id})[0] == 200
    assert session_id not in app.sessions


def test_unknown_routes_return_404(serve) -> None:
    port, _ = serve([])
    assert request(port, "GET", "/api/nope")[0] == 404
    assert request(port, "POST", "/api/nope", {})[0] == 404
