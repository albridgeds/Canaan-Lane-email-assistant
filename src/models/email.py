"""Email data models."""
from __future__ import annotations

from pydantic import BaseModel, Field


class EmailDecision(BaseModel):
    """LLM decision about an email."""

    action_required: bool
    importance: str
    action: str | None = None
    deadline: str | None = None
    summary: str
    reason: str
    links: list[str] = Field(default_factory=list)
    should_notify: bool


class GmailMessage:
    """Parsed Gmail message."""

    def __init__(
        self,
        *,
        gmail_id: str,
        thread_id: str,
        subject: str,
        sender: str,
        date: str,
        body_text: str,
        snippet: str,
    ) -> None:
        self.gmail_id = gmail_id
        self.thread_id = thread_id
        self.subject = subject
        self.sender = sender
        self.date = date
        self.body_text = body_text
        self.snippet = snippet

