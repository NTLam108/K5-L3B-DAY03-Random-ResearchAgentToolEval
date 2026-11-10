from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _escape_intraword_underscores(text: str) -> str:
    """Legacy Telegram Markdown treats `_` as italics, so `send_telegram` would show as "sendtelegram".

    Only underscores between word characters are escaped; deliberate `_italic_` markup is left alone.
    """
    return re.sub(r"(?<=\w)_(?=\w)", r"\\_", text)


def send_telegram(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    if not confirmed:
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": _escape_intraword_underscores(text), "parse_mode": "Markdown"},
            timeout=TIMEOUT,
        )
        if response.status_code == 400:
            # Telegram rejects text it cannot parse as Markdown (e.g. a stray `*` or `_`): resend as plain text
            # so the message is not lost.
            response = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=TIMEOUT)
        response.raise_for_status()
        return {"tool": "send_telegram", "status": "sent"}
    except Exception as exc:
        return err("send_telegram", exc)

