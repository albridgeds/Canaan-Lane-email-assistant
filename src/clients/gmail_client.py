"""Gmail API client."""
from __future__ import annotations

import base64
import os.path
import re
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.models.email import GmailMessage


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailClient:
    """Client for interacting with Gmail API."""

    def __init__(self, credentials_path: str, token_path: str) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._build_service()

    def _build_service(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def _find_label_id(self, label_name: str) -> str:
        """Find Gmail label ID by name."""
        labels = self.service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"] == label_name:
                return label["id"]
        raise ValueError(f"Gmail label '{label_name}' not found.")

    def list_unprocessed_messages(self, label_name: str, max_results: int = 10) -> list[dict[str, str]]:
        """List messages in a Gmail label."""
        label_id = self._find_label_id(label_name)
        response = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                labelIds=[label_id],
                maxResults=max_results,
                q="category:primary OR category:updates OR category:forums",
            )
            .execute()
        )
        return response.get("messages", [])

    def get_message(self, gmail_id: str) -> GmailMessage:
        """Fetch and parse a Gmail message."""
        raw = (
            self.service.users()
            .messages()
            .get(userId="me", id=gmail_id, format="full")
            .execute()
        )

        payload = raw.get("payload", {})
        headers = payload.get("headers", [])

        subject = self._header(headers, "Subject")
        sender = self._header(headers, "From")
        date = self._header(headers, "Date")

        body_text = self._extract_text(payload).strip()
        snippet = raw.get("snippet", "")

        return GmailMessage(
            gmail_id=raw["id"],
            thread_id=raw["threadId"],
            subject=subject,
            sender=sender,
            date=date,
            body_text=body_text or snippet,
            snippet=snippet,
        )

    def _header(self, headers: list[dict[str, str]], name: str) -> str:
        """Extract header value by name."""
        for header in headers:
            if header.get("name", "").lower() == name.lower():
                return header.get("value", "")
        return ""

    def _extract_text(self, payload: dict[str, Any]) -> str:
        """Extract text content from message payload."""
        mime_type = payload.get("mimeType", "")
        body = payload.get("body", {})

        if mime_type == "text/plain":
            data = body.get("data")
            return self._decode_base64(data) if data else ""

        if mime_type == "text/html":
            data = body.get("data")
            html = self._decode_base64(data) if data else ""
            return self._strip_html(html)

        parts = payload.get("parts", [])
        texts: list[str] = []

        for part in parts:
            part_type = part.get("mimeType", "")
            if part_type == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    texts.append(self._decode_base64(data))
            elif part_type == "text/html":
                data = part.get("body", {}).get("data")
                if data:
                    texts.append(self._strip_html(self._decode_base64(data)))
            elif "parts" in part:
                nested = self._extract_text(part)
                if nested:
                    texts.append(nested)

        return "\n".join(t for t in texts if t).strip()

    def _decode_base64(self, data: str) -> str:
        """Decode base64 data."""
        padded = data.replace("-", "+").replace("_", "/")
        decoded = base64.b64decode(padded)
        return decoded.decode("utf-8", errors="replace")

    def _strip_html(self, html: str) -> str:
        """Strip HTML tags and clean text."""
        text = re.sub(r"(?is)<(script|style).*?>.*?(</\\1>)", " ", html)
        text = re.sub(r"(?s)<.*?>", " ", text)
        text = re.sub(r"\\s+", " ", text)
        return text.strip()

