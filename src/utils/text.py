"""Text utilities."""
from __future__ import annotations

import html
import re


URL_RE = re.compile(r"https?://\S+")

_IMPORTANCE_ICON = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
}


def extract_links(text: str) -> list[str]:
    """Extract unique URLs from text."""
    return list(dict.fromkeys(URL_RE.findall(text)))


def _e(value: str | None) -> str:
    """Escape a user-provided string for safe use inside Telegram HTML messages."""
    return html.escape(value or "—", quote=False)


def format_notification(message, decision) -> str:
    """Format email decision as a user-friendly HTML notification for Telegram."""
    importance_raw = (decision.importance or "").lower()
    importance_icon = _IMPORTANCE_ICON.get(importance_raw, "📋")

    lines = [
        "📧 <b>New email received</b>",
        "",
        f"📅 <b>Date:</b> {_e(message.date)[:-15]}",
        f"📌 <b>Topic:</b> {_e(message.subject)}",
        f"{importance_icon} <b>Importance:</b> {_e(decision.importance)}",
    ]

    if decision.action:
        lines.append(f"⚡ <b>Action:</b> {_e(decision.action)}")

    if decision.summary:
        lines += ["", f"💬 {_e(decision.summary)}"]

    if decision.deadline:
        lines += ["", f"⏰ <b>Deadline:</b> {_e(decision.deadline)}"]

    if decision.links:
        links_text = "\n".join(
            f'  • <a href="{html.escape(url, quote=True)}">{html.escape(url)}</a>'
            for url in decision.links
        )
        lines += ["", f"🔗 <b>Links:</b>\n{links_text}"]

    return "\n".join(lines)
