"""OpenAI LLM client."""
from __future__ import annotations

import json
from typing import Any

import requests
from pydantic import ValidationError

from src.models.email import EmailDecision
from src.utils.prompts import CLASSIFICATION_PROMPT


class LLMClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def classify_email(
        self,
        *,
        subject: str,
        sender: str,
        date: str,
        body_text: str,
    ) -> EmailDecision:
        """Classify email using LLM."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is missing.")

        user_content = f"""
Subject: {subject}
From: {sender}
Date: {date}

Email body:
{body_text[:12000]}
""".strip()

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": CLASSIFICATION_PROMPT},
                    {"role": "user", "content": user_content},
                ],
            },
            timeout=60,
        )
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(content)
            print(parsed)
            return EmailDecision.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ValueError(f"Failed to parse LLM response: {exc}\nRaw content: {content}") from exc

