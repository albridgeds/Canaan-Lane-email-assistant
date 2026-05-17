"""Utility for viewing processed email records from assistant.db.

Usage:
    python scripts/view_db.py               # show all records
    python scripts/view_db.py --limit 10    # show last 10 records
    python scripts/view_db.py --search text # filter by subject (case-insensitive)
    python scripts/view_db.py --notify-only # show only records where should_notify=True
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.clients.storage import Storage

SEPARATOR = "=" * 72


def print_records(records: list[dict]) -> None:
    """Print records in a formatted table."""
    if not records:
        print("No records found.")
        return

    for i, r in enumerate(records, start=1):
        links_str = ", ".join(r["links"]) if r["links"] else "-"
        print(SEPARATOR)
        print(f"  Record #{i}  |  processed_at: {r['processed_at']}")
        print(SEPARATOR)
        print(f"  gmail_id        : {r['gmail_id']}")
        print(f"  subject         : {r['subject'] or '-'}")
        print(f"  sender          : {r['sender'] or '-'}")
        print(f"  email_date      : {r['email_date'] or '-'}")
        print(f"  importance      : {r['importance'] or '-'}")
        print(f"  action_required : {'yes' if r['action_required'] else 'no'}")
        print(f"  action          : {r['action'] or '-'}")
        print(f"  deadline        : {r['deadline'] or '-'}")
        print(f"  should_notify   : {'yes' if r['should_notify'] else 'no'}")
        print(f"  links           : {links_str}")
        print(f"  summary         :\n    {r['summary'] or '-'}")
        print(f"  reason          :\n    {r['reason'] or '-'}")

    print(SEPARATOR)
    print(f"Total records: {len(records)}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="View processed email records from assistant.db"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of records to display",
    )
    parser.add_argument(
        "--search",
        type=str,
        default=None,
        help="Filter by subject (case-insensitive)",
    )
    parser.add_argument(
        "--notify-only",
        action="store_true",
        help="Show only records where should_notify is True",
    )
    args = parser.parse_args()

    storage = Storage(settings.sqlite_path)
    records = storage.get_all_processed()

    if args.search:
        keyword = args.search.lower()
        records = [r for r in records if keyword in (r["subject"] or "").lower()]

    if args.notify_only:
        records = [r for r in records if r["should_notify"]]

    if args.limit is not None:
        records = records[: args.limit]

    print_records(records)


if __name__ == "__main__":
    main()

