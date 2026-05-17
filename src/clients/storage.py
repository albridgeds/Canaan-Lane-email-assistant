"""Database storage client."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager


class Storage:
    """SQLite database storage client."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_emails (
                    gmail_id        TEXT PRIMARY KEY,
                    subject         TEXT,
                    sender          TEXT,
                    email_date      TEXT,
                    action_required INTEGER,
                    importance      TEXT,
                    action          TEXT,
                    deadline        TEXT,
                    summary         TEXT,
                    reason          TEXT,
                    links           TEXT,
                    should_notify   INTEGER,
                    processed_at    DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            # migrate: add columns if they don't exist yet (for existing DBs)
            existing = {
                row[1]
                for row in conn.execute("PRAGMA table_info(processed_emails)").fetchall()
            }
            new_columns = {
                "sender":          "TEXT",
                "email_date":      "TEXT",
                "action_required": "INTEGER",
                "importance":      "TEXT",
                "action":          "TEXT",
                "deadline":        "TEXT",
                "summary":         "TEXT",
                "reason":          "TEXT",
                "links":           "TEXT",
                "should_notify":   "INTEGER",
            }
            for col, col_type in new_columns.items():
                if col not in existing:
                    conn.execute(
                        f"ALTER TABLE processed_emails ADD COLUMN {col} {col_type}"
                    )

    def is_processed(self, gmail_id: str) -> bool:
        """Check if an email has been processed."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_emails WHERE gmail_id = ?",
                (gmail_id,),
            ).fetchone()
        return row is not None

    def mark_processed(self, gmail_id: str, subject: str) -> None:
        """Mark an email as processed."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_emails (gmail_id, subject) VALUES (?, ?)",
                (gmail_id, subject),
            )

    def save_email_result(
        self,
        *,
        gmail_id: str,
        subject: str,
        sender: str,
        email_date: str,
        action_required: bool,
        importance: str,
        action: str | None,
        deadline: str | None,
        summary: str,
        reason: str,
        links: list[str],
        should_notify: bool,
    ) -> None:
        """Insert or replace a fully processed email record with all LLM output fields."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO processed_emails
                    (gmail_id, subject, sender, email_date,
                     action_required, importance, action, deadline,
                     summary, reason, links, should_notify)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(gmail_id) DO UPDATE SET
                    subject         = excluded.subject,
                    sender          = excluded.sender,
                    email_date      = excluded.email_date,
                    action_required = excluded.action_required,
                    importance      = excluded.importance,
                    action          = excluded.action,
                    deadline        = excluded.deadline,
                    summary         = excluded.summary,
                    reason          = excluded.reason,
                    links           = excluded.links,
                    should_notify   = excluded.should_notify
                """,
                (
                    gmail_id,
                    subject,
                    sender,
                    email_date,
                    int(action_required),
                    importance,
                    action,
                    deadline,
                    summary,
                    reason,
                    json.dumps(links),
                    int(should_notify),
                ),
            )

    def get_all_processed(self) -> list[dict]:
        """Return all processed email records ordered by most recent first."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT gmail_id, subject, sender, email_date,
                       action_required, importance, action, deadline,
                       summary, reason, links, should_notify, processed_at
                FROM processed_emails
                ORDER BY processed_at DESC
                """
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["action_required"] = bool(d["action_required"])
            d["should_notify"] = bool(d["should_notify"])
            try:
                d["links"] = json.loads(d["links"]) if d["links"] else []
            except (json.JSONDecodeError, TypeError):
                d["links"] = []
            result.append(d)
        return result

