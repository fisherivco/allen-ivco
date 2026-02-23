#!/usr/bin/env python3
"""Codex inbox watcher.

Detect unread messages from claude-code in shared-state inbox.
Prints a concise alert when unread messages exist.
No output when no unread messages are found.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

INBOX_DIR = Path(
    os.environ.get(
        "CODEX_INBOX_DIR",
        str(Path.home() / "AI-Workspace" / "shared-state" / "inbox" / "codex-cli"),
    )
)
LOG_FILE = Path(
    os.environ.get(
        "CODEX_INBOX_WATCHER_LOG",
        str(
            Path.home()
            / "AI-Workspace"
            / "memory"
            / "debug-log"
            / "raw"
            / "codex-inbox-watcher.log"
        ),
    )
)
FROM_FILTER = os.environ.get("CODEX_INBOX_FROM", "claude-code")
STATUS_FILTER = "unread"


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        if isinstance(data, dict):
            return data
        return None
    except (OSError, json.JSONDecodeError):
        return None


def _collect_unread() -> list[dict[str, str]]:
    unread: list[dict[str, str]] = []
    if not INBOX_DIR.is_dir():
        return unread

    for file in sorted(INBOX_DIR.glob("*.json")):
        data = _load_json(file)
        if not data:
            continue
        meta = data.get("_meta", {})
        if not isinstance(meta, dict):
            continue

        sender = str(meta.get("from", ""))
        status = str(meta.get("status", ""))
        if sender != FROM_FILTER or status != STATUS_FILTER:
            continue

        unread.append(
            {
                "file": file.name,
                "timestamp": str(meta.get("timestamp", "")),
                "subject": str(data.get("subject", "(no subject)")),
                "type": str(meta.get("type", "")),
            }
        )

    return unread


def _log_detection(count: int, subjects: list[str]) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} unread_from={FROM_FILTER} count={count} subjects={'; '.join(subjects)}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


def main() -> int:
    unread = _collect_unread()
    if not unread:
        return 0  # fast path: silent exit

    subjects = [m["subject"] for m in unread]
    _log_detection(len(unread), subjects)

    print(f"[inbox-watcher] unread from {FROM_FILTER}: {len(unread)}")
    for m in unread:
        ts = m["timestamp"] or "--:--"
        msg_type = f"{m['type']}" if m["type"] else "message"
        print(f"- [{ts}] ({msg_type}) {m['subject']} [{m['file']}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
