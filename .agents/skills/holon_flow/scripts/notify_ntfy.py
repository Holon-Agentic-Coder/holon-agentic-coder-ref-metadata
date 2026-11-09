#!/usr/bin/env python3
"""Send a push notification through ntfy.sh (free, no account) so a long flow can tell the maintainer it has finished.

The topic acts as a password: anyone who knows it can read the messages, so it is read from
``HOLON_NTFY_TOPIC`` or ``~/.holon/secrets/ntfy-topic`` and never printed or committed. Messages stay on the ntfy server
for a while, so keep them generic: slugs, PR numbers and verdicts only, never secrets or file contents.

Usage:
    notify_ntfy.py "Title" "Message" [--priority high] [--tags white_check_mark]

When no topic is configured, or the server cannot be reached, it does nothing and exits 0, so a notification can never
fail a flow.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_SERVER = "https://ntfy.sh"
TOPIC_FILE = Path.home() / ".holon" / "secrets" / "ntfy-topic"
TIMEOUT_SECONDS = 10


def read_topic() -> str | None:
    """Return the configured topic, or None when notifications are not set up."""
    topic = os.environ.get("HOLON_NTFY_TOPIC", "").strip()
    if not topic and TOPIC_FILE.is_file():
        topic = TOPIC_FILE.read_text(encoding="utf-8").strip()
    return topic or None


def _ascii(value: str) -> str:
    """HTTP header values must be Latin-1; keep titles plain ASCII."""
    return value.encode("ascii", "replace").decode("ascii")


def notify(title: str, message: str, priority: str = "default", tags: str = "") -> bool:
    """Publish a notification; return True when the server accepted it. Never raises."""
    topic = read_topic()
    if topic is None:
        return False
    server = os.environ.get("HOLON_NTFY_SERVER", DEFAULT_SERVER).rstrip("/")
    headers = {"Title": _ascii(title), "Priority": priority}
    if tags:
        headers["Tags"] = tags
    request = urllib.request.Request(  # noqa: S310 - fixed https server, topic from private config
        f"{server}/{topic}", data=message.encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310
            return 200 <= response.status < 300
    except (urllib.error.URLError, OSError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a push notification through ntfy.sh.")
    parser.add_argument("title")
    parser.add_argument("message")
    parser.add_argument("--priority", default="default", choices=["min", "low", "default", "high", "urgent"])
    parser.add_argument("--tags", default="", help="Comma-separated ntfy tags or emoji names, e.g. white_check_mark")
    args = parser.parse_args()
    sent = notify(args.title, args.message, args.priority, args.tags)
    print("notification sent" if sent else "notification not sent (no topic configured or server unreachable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
