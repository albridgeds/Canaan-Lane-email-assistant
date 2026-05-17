"""Main email assistant application."""
from __future__ import annotations

import logging

from src.config import settings
from src.clients.gmail_client import GmailClient
from src.clients.llm_client import LLMClient
from src.clients.storage import Storage
from src.clients.telegram import TelegramNotifier
from src.utils.text import extract_links, format_notification


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def main() -> None:
    """Main entry point for email processing."""
    storage = Storage(settings.sqlite_path)
    gmail = GmailClient(
        credentials_path=settings.gmail_credentials_path,
        token_path=settings.gmail_token_path,
    )
    llm = LLMClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    notifier = TelegramNotifier(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )

    notify_all = settings.notification_mode == "all"
    notify_important_only = settings.notification_mode in {"important_only", "important"}

    if not (notify_all or notify_important_only):
        raise ValueError(
            "Invalid NOTIFICATION_MODE. Use 'important_only' or 'all'."
        )

    logging.info("Checking Gmail label: %s", settings.gmail_label)
    messages = gmail.list_unprocessed_messages(settings.gmail_label, max_results=10)

    if not messages:
        logging.info("No messages found.")
        return

    for item in messages:
        print(f"Processing email ID: {item['id']}")
        gmail_id = item["id"]

        if storage.is_processed(gmail_id):
            logging.info("Skipping already processed email: %s", gmail_id)
            continue

        try:
            message = gmail.get_message(gmail_id)
            body = message.body_text or message.snippet

            decision = llm.classify_email(
                subject=message.subject,
                sender=message.sender,
                date=message.date,
                body_text=body,
            )

            if not decision.links:
                decision.links = extract_links(body)

            should_send = decision.should_notify if notify_important_only else True

            if should_send:
                text = format_notification(message, decision)
                notifier.send_message(text)
                logging.info("Notification sent for: %s", message.subject)
            else:
                logging.info("No notification needed: %s", message.subject)

            storage.save_email_result(
                gmail_id=gmail_id,
                subject=message.subject,
                sender=message.sender,
                email_date=message.date,
                action_required=decision.action_required,
                importance=decision.importance,
                action=decision.action,
                deadline=decision.deadline,
                summary=decision.summary,
                reason=decision.reason,
                links=decision.links,
                should_notify=decision.should_notify,
            )

        except Exception as exc:
            logging.exception("Failed to process email %s: %s", gmail_id, exc)


if __name__ == "__main__":
    main()
