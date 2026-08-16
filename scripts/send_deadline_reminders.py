"""Send one aggregated Telegram reminder for deadlines due tomorrow."""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Protocol

from src.config import settings
from src.clients.storage import Storage
from src.clients.telegram import TelegramNotifier
from src.utils.text import format_deadline_digest


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

REMINDER_TYPE = "deadline_tomorrow_digest"


class _NotifierProtocol(Protocol):
    def send_message(self, text: str) -> None:
        ...


def _tomorrow_iso() -> str:
    """Return tomorrow date in ISO format (YYYY-MM-DD)."""
    return (date.today() + timedelta(days=1)).isoformat()


def _send_to_channel(
    storage: Storage,
    notifier: _NotifierProtocol,
    *,
    channel_name: str,
    reminder_date: str,
    text: str,
) -> bool:
    """Send reminder to a channel once per date; return True if sent this run."""
    if storage.was_reminder_sent(REMINDER_TYPE, reminder_date, channel_name):
        logging.info("Reminder already sent for %s channel on %s", channel_name, reminder_date)
        return False

    notifier.send_message(text)
    storage.mark_reminder_sent(REMINDER_TYPE, reminder_date, channel_name)
    logging.info("Reminder sent to %s channel for %s", channel_name, reminder_date)
    return True


def main() -> None:
    """Main entry point for daily deadline reminders."""
    storage = Storage(settings.sqlite_path)
    reminder_date = _tomorrow_iso()
    records = storage.get_deadlines_for_date(reminder_date)

    if not records:
        logging.info("No notifiable deadlines found for %s", reminder_date)
        return

    text = format_deadline_digest(reminder_date, records)

    main_notifier = TelegramNotifier(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )
    _send_to_channel(
        storage,
        main_notifier,
        channel_name="main",
        reminder_date=reminder_date,
        text=text,
    )

    debug_chat_id = settings.telegram_debug_chat_id.strip()
    if debug_chat_id:
        debug_notifier = TelegramNotifier(
            bot_token=settings.telegram_bot_token,
            chat_id=debug_chat_id,
        )
        _send_to_channel(
            storage,
            debug_notifier,
            channel_name="debug",
            reminder_date=reminder_date,
            text=text,
        )
    else:
        logging.info("Debug chat id is empty, debug reminder is skipped.")


if __name__ == "__main__":
    main()


