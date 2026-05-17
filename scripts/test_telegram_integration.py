"""Integration test for Telegram notification using the latest DB subject."""
from __future__ import annotations

import json
import sqlite3
from types import SimpleNamespace

import pytest
import requests

from src.config import settings
from src.clients.storage import Storage
from src.clients.telegram import TelegramNotifier
from src.utils.text import format_notification


def _latest_record_from_db(db_path: str) -> dict:
    """Return the latest fully-populated record from processed_emails."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT subject, sender, email_date,
                   importance, action, deadline, summary, links, should_notify
            FROM processed_emails
            WHERE subject IS NOT NULL AND TRIM(subject) != ''
            ORDER BY processed_at DESC
            LIMIT 1
            """
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise RuntimeError(
            "No notification entry with a non-empty subject found in processed_emails."
        )

    record = dict(row)
    try:
        record["links"] = json.loads(record["links"]) if record["links"] else []
    except (json.JSONDecodeError, TypeError):
        record["links"] = []
    return record


def test_telegram_integration() -> None:
    """Send a real Telegram message in the current notification format using the latest DB record."""
    db_path = settings.sqlite_path
    bot_token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id.strip()

    if not bot_token or not chat_id:
        pytest.skip("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to run Telegram integration test.")

    Storage(db_path)

    record = _latest_record_from_db(db_path)
    print("record:", record)

    # Build lightweight message/decision objects matching format_notification signature.
    message = SimpleNamespace(
        date=record.get("email_date"),
        subject=record.get("subject"),
    )
    decision = SimpleNamespace(
        importance=record.get("importance"),
        action=record.get("action"),
        summary=record.get("summary"),
        deadline=record.get("deadline"),
        links=record.get("links", []),
    )

    text = format_notification(message, decision)
    print("text:", text)
    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)

    try:
        notifier.send_message(text)
    except requests.HTTPError as exc:
        body = ""
        if exc.response is not None:
            try:
                body = exc.response.text
            except Exception:
                body = "<failed to read response body>"
        pytest.fail(f"Telegram sendMessage failed: {exc}. Response body: {body}")


if __name__ == "__main__":
    test_telegram_integration()