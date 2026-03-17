#!/usr/bin/env python3
"""Codex notify hook — runs after every agent turn.

Checks for unread inbox messages and sends macOS notification if any exist.
Designed to be fast (<100ms) since it runs after every Codex turn.

Usage in ~/.codex/config.toml:
  notify = ["python3", "/Users/allenchenmac/fisher/projects/allen-ivco/scripts/codex_inbox_notify.py"]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

INBOX_DIR = Path.home() / "fisher" / "shared-state" / "inbox" / "codex-cli"
LOG_FILE = (
    Path.home()
    / "fisher"
    / "shared-state"
    / "contributions"
    / "codex"
    / "logs"
    / "codex-inbox-notify.log"
)


def count_unread() -> tuple[int, list[str]]:
    """Count unread messages and return (count, subject_list)."""
    if not INBOX_DIR.is_dir():
        return 0, []

    count = 0
    subjects: list[str] = []
    for f in sorted(INBOX_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            meta = data.get("_meta", {})
            if isinstance(meta, dict) and meta.get("status") == "unread":
                count += 1
                subjects.append(str(data.get("subject", "(no subject)")))
        except (OSError, json.JSONDecodeError):
            continue

    return count, subjects


def notify_macos(title: str, message: str) -> None:
    """Send macOS notification via osascript (always available)."""
    # Escape double quotes for AppleScript
    safe_msg = message.replace('"', '\\"')
    safe_title = title.replace('"', '\\"')
    script = f'display notification "{safe_msg}" with title "{safe_title}"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass  # Non-critical — don't block Codex


def log_event(count: int) -> None:
    """Append detection event to log file."""
    from datetime import datetime

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{ts} notify_hook unread={count}\n")


def main() -> int:
    count, subjects = count_unread()
    if count == 0:
        return 0  # Silent exit — no notification needed

    # Build summary
    summary = f"{count} unread message{'s' if count > 1 else ''}"
    if subjects:
        summary += f": {subjects[0]}"
        if count > 1:
            summary += f" (+{count - 1} more)"

    # Send macOS notification to Allen
    notify_macos("Jack Inbox", summary)

    # Log for audit trail
    log_event(count)

    # Also print to stdout (visible in Codex logs if captured)
    print(f"[inbox-notify] {summary}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
