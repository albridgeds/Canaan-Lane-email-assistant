"""Telegram notifier client."""
from __future__ import annotations

import requests


class TelegramNotifier:
    """Client for sending notifications via Telegram."""

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text: str) -> None:
        """Send a message via Telegram."""
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram credentials are missing.")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        response.raise_for_status()

