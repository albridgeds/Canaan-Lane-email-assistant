from __future__ import annotations

from pathlib import Path

from src.clients.storage import Storage
from src.utils.text import format_deadline_digest


REMINDER_TYPE = "deadline_tomorrow_digest"


def _make_storage(tmp_path: Path) -> Storage:
    return Storage(str(tmp_path / "test.db"))


def _insert_record(
    storage: Storage,
    *,
    gmail_id: str,
    subject: str,
    deadline: str | None,
    should_notify: bool,
    importance: str = "medium",
) -> None:
    storage.save_email_result(
        gmail_id=gmail_id,
        subject=subject,
        sender="school@example.com",
        email_date="Mon, 10 Aug 2026 09:00:00 +0000",
        action_required=True,
        importance=importance,
        action="Submit form",
        deadline=deadline,
        summary="Please submit the form.",
        reason="Action required",
        links=["https://example.com/form"],
        should_notify=should_notify,
    )


def test_get_deadlines_for_date_returns_only_notifiable_records(tmp_path: Path) -> None:
    storage = _make_storage(tmp_path)

    _insert_record(
        storage,
        gmail_id="1",
        subject="Should be included",
        deadline="2026-08-17",
        should_notify=True,
        importance="high",
    )
    _insert_record(
        storage,
        gmail_id="2",
        subject="Wrong date",
        deadline="2026-08-18",
        should_notify=True,
    )
    _insert_record(
        storage,
        gmail_id="3",
        subject="Not notifiable",
        deadline="2026-08-17",
        should_notify=False,
    )

    rows = storage.get_deadlines_for_date("2026-08-17")

    assert len(rows) == 1
    assert rows[0]["gmail_id"] == "1"
    assert rows[0]["subject"] == "Should be included"


def test_reminder_log_is_idempotent_per_day(tmp_path: Path) -> None:
    storage = _make_storage(tmp_path)
    reminder_date = "2026-08-17"
    assert storage.was_reminder_sent(REMINDER_TYPE, reminder_date, "main") is False

    storage.mark_reminder_sent(REMINDER_TYPE, reminder_date, "main")
    storage.mark_reminder_sent(REMINDER_TYPE, reminder_date, "main")

    assert storage.was_reminder_sent(REMINDER_TYPE, reminder_date, "main") is True


def test_format_deadline_digest_contains_expected_fields() -> None:
    rows = [
        {
            "subject": "Math camp payment",
            "importance": "high",
            "action": "Pay invoice",
            "sender": "School Office",
            "links": ["https://example.com/pay"],
        },
        {
            "subject": "Bring costume",
            "importance": "medium",
            "action": None,
            "sender": "Teacher",
            "links": [],
        },
    ]

    text = format_deadline_digest("2026-08-17", rows)

    assert "deadlines tomorrow" in text
    assert "2026-08-17" in text
    assert "Total tasks: <b>2</b>" in text
    assert "Math camp payment" in text
    assert "Bring costume" in text


