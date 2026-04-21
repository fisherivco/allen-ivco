#!/usr/bin/env python3
"""Codex inbox watcher with Agent Bus communication queue awareness."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INBOX_DIR = Path(
    os.environ.get(
        "CODEX_INBOX_DIR",
        str(Path.home() / "fisher" / "shared-state" / "inbox" / "codex-cli"),
    )
)
WORKSPACE_ROOT = Path(
    os.environ.get(
        "AGENT_BUS_WORKSPACE",
        "/Users/allenchenmac/fisher",
    )
)
BUS_PENDING_DIR = WORKSPACE_ROOT / "shared-state" / "agent-bus" / "tasks" / "pending"
BUS_MESSAGES_DIR = WORKSPACE_ROOT / "shared-state" / "agent-bus" / "tasks" / "messages"
BUS_IN_PROGRESS_DIR = WORKSPACE_ROOT / "shared-state" / "agent-bus" / "tasks" / "in-progress"
TRIGGER_FILE = Path(
    os.environ.get(
        "CODEX_INBOX_TRIGGER",
        str(Path.home() / "fisher" / "shared-state" / "inbox" / "codex-cli" / ".trigger"),
    )
)
LOG_FILE = Path(
    os.environ.get(
        "CODEX_INBOX_WATCHER_LOG",
        str(
            Path.home()
            / "fisher"
            / "shared-state"
            / "contributions"
            / "codex"
            / "logs"
            / "codex-inbox-watcher.log"
        ),
    )
)
DIGEST_FILE = INBOX_DIR / ".inbox-digest.json"
STATUS_FILTER = "unread"


def _parse_iso_ts(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _count_inbox_total() -> int:
    if not INBOX_DIR.is_dir():
        return 0
    return sum(1 for f in INBOX_DIR.glob("*.json") if not f.name.startswith("."))


def _write_trigger(
    *,
    unread_count: int,
    inbox_total: int,
    newest_subject: str,
    comm_pending: int,
    comm_in_progress: int,
) -> None:
    """Write a trigger file for active sessions to detect new messages.

    The trigger file is a lightweight signal — active sessions poll this file
    to know when new messages arrive without scanning the full inbox.
    """
    trigger_data = {
        "unread_count": unread_count,
        "inbox_unread": unread_count,
        "inbox_total": inbox_total,
        "comm_pending": comm_pending,
        "comm_in_progress": comm_in_progress,
        "newest_subject": newest_subject,
        "triggered_at": datetime.now().isoformat(),
        "watcher_pid": os.getpid(),
    }
    TRIGGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRIGGER_FILE.write_text(
        json.dumps(trigger_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _clear_trigger() -> None:
    """Remove trigger file when no unread messages exist."""
    if TRIGGER_FILE.exists():
        TRIGGER_FILE.unlink(missing_ok=True)


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
        if status != STATUS_FILTER:
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


def _collect_comm_tasks(task_dir: Path) -> list[dict[str, str]]:
    comm_tasks: list[dict[str, str]] = []
    if not task_dir.is_dir():
        return comm_tasks

    for file in sorted(task_dir.glob("*.task.json")):
        data = _load_json(file)
        if not data:
            continue
        if str(data.get("task_kind", "")).strip() != "communication":
            continue

        communication = data.get("communication", {})
        if not isinstance(communication, dict):
            communication = {}

        subject = str(communication.get("subject") or data.get("title") or "(no subject)")
        created_at = str(data.get("created_at", "")).strip()
        comm_tasks.append(
            {
                "file": file.name,
                "subject": subject,
                "created_at": created_at,
            }
        )

    return comm_tasks


def _pick_newest_subject(unread: list[dict[str, str]], comm_pending: list[dict[str, str]]) -> str:
    candidates: list[tuple[datetime | None, str, str]] = []

    for msg in unread:
        candidates.append(
            (
                _parse_iso_ts(str(msg.get("timestamp", ""))),
                str(msg.get("file", "")),
                str(msg.get("subject", "(no subject)")),
            )
        )
    for task in comm_pending:
        candidates.append(
            (
                _parse_iso_ts(str(task.get("created_at", ""))),
                str(task.get("file", "")),
                str(task.get("subject", "(no subject)")),
            )
        )

    if not candidates:
        return ""

    # Prefer parseable timestamps; fallback to filename ordering.
    best = max(
        candidates,
        key=lambda item: (
            1 if item[0] is not None else 0,
            item[0].timestamp() if item[0] is not None else float("-inf"),
            item[1],
        ),
    )
    return best[2]


def _write_digest(
    messages: list[dict[str, str]],
    *,
    inbox_total: int,
    comm_pending: int,
    comm_in_progress: int,
    newest_subject: str,
) -> None:
    """Write a structured JSON digest for Codex CLI to consume at session start."""
    now = datetime.now().isoformat()
    unread_count = len(messages)
    latest_subjects = [str(m.get("subject", "(no subject)")) for m in messages[-5:]]
    extra_subjects = max(0, unread_count - len(latest_subjects))
    digest = {
        "unread_count": unread_count,
        "inbox_unread": unread_count,
        "inbox_total": inbox_total,
        "comm_pending": comm_pending,
        "comm_in_progress": comm_in_progress,
        "newest_subject": newest_subject,
        "latest_subjects": latest_subjects,
        "extra_subjects": extra_subjects,
        "messages": messages,
        "last_checked": now,
        "digest_created": now,
    }
    DIGEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    DIGEST_FILE.write_text(json.dumps(digest, indent=2, ensure_ascii=False), encoding="utf-8")


def _log_detection(count: int, subjects: list[str]) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} unread_count={count} subjects={'; '.join(subjects)}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


def main() -> int:
    unread = _collect_unread()
    inbox_total = _count_inbox_total()
    messages_comm_tasks = _collect_comm_tasks(BUS_MESSAGES_DIR)
    # Transition fallback: still scan pending/ until all COMM tasks are migrated.
    pending_comm_tasks = _collect_comm_tasks(BUS_PENDING_DIR)
    queued_comm_tasks = messages_comm_tasks + pending_comm_tasks
    in_progress_comm_tasks = _collect_comm_tasks(BUS_IN_PROGRESS_DIR)
    comm_pending = len(queued_comm_tasks)
    comm_in_progress = len(in_progress_comm_tasks)

    if not unread and comm_pending == 0 and comm_in_progress == 0:
        _clear_trigger()
        _write_digest(
            [],
            inbox_total=inbox_total,
            comm_pending=0,
            comm_in_progress=0,
            newest_subject="",
        )
        return 0

    newest_subject = _pick_newest_subject(unread, queued_comm_tasks)
    subjects = [m["subject"] for m in unread]
    _write_trigger(
        unread_count=len(unread),
        inbox_total=inbox_total,
        newest_subject=newest_subject,
        comm_pending=comm_pending,
        comm_in_progress=comm_in_progress,
    )
    _write_digest(
        unread,
        inbox_total=inbox_total,
        comm_pending=comm_pending,
        comm_in_progress=comm_in_progress,
        newest_subject=newest_subject,
    )
    if unread:
        _log_detection(len(unread), subjects)

    if unread:
        print(f"[inbox-watcher] unread: {len(unread)}")
        for m in unread:
            ts = m["timestamp"] or "--:--"
            msg_type = f"{m['type']}" if m["type"] else "message"
            print(f"- [{ts}] ({msg_type}) {m['subject']} [{m['file']}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
