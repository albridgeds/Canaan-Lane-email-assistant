"""Application configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / "config" / "secret.env", override=False)
load_dotenv(ROOT_DIR / "config" / "public.env", override=False)


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    gmail_label: str = os.getenv("GMAIL_LABEL", "School")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    notification_mode: str = os.getenv("NOTIFICATION_MODE", "all").lower()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    sqlite_path: str = os.getenv("SQLITE_PATH", "assistant.db")
    gmail_credentials_path: str = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
    gmail_token_path: str = os.getenv("GMAIL_TOKEN_PATH", "token.json")


settings = Settings()
