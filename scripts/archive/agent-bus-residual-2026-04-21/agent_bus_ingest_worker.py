#!/usr/bin/env python3
"""Ingest new Obsidian inbox notes into Allen Agent Bus.

Designed for launchd periodic execution (single pass, then exit).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HOME = Path.home()
ROOT = HOME / "fisher"
OBSIDIAN_INBOX = HOME / "Vaults" / "Obsidian" / "inbox"
BUS_DIR = ROOT / "shared-state" / "agent-bus"
BUS_INBOX = BUS_DIR / "inbox"
BUS_STATUS = BUS_DIR / "status"
STATE_FILE = BUS_STATUS / "obsidian-ingest-state.json"
JANE_INBOX = ROOT / "shared-state" / "inbox" / "claude-code"
LOG_FILE = ROOT / "shared-state" / "contributions" / "codex" / "logs" / "agent-bus-ingest-worker.log"
IGNORE_NAMES = {"index.md", "README.md"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def now_local() -> datetime:
    return datetime.now().astimezone()


def slugify(value: str, max_len: int = 32) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower())
    out = re.sub(r"-{2,}", "-", out).strip("-")
    return (out or "item")[:max_len].strip("-")


def ensure_dirs() -> None:
    for d in (BUS_INBOX, BUS_STATUS, JANE_INBOX, LOG_FILE.parent):
        d.mkdir(parents=True, exist_ok=True)


def log_line(message: str) -> None:
    ts = now_local().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{ts} {message}\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_state() -> dict[str, Any]:
    if not STATE_FILE.is_file():
        return {
            "bootstrapped": False,
            "known_files": [],
            "last_run_at": None,
            "last_ingested_count": 0,
        }
    try:
        state = read_json(STATE_FILE)
        if isinstance(state, dict):
            return state
    except json.JSONDecodeError:
        pass
    return {
        "bootstrapped": False,
        "known_files": [],
        "last_run_at": None,
        "last_ingested_count": 0,
    }


def save_state(state: dict[str, Any]) -> None:
    state["last_run_at"] = now_iso()
    write_json(STATE_FILE, state)


def list_obsidian_files() -> list[Path]:
    if not OBSIDIAN_INBOX.is_dir():
        return []
    files = []
    for path in sorted(OBSIDIAN_INBOX.glob("*.md")):
        if path.name.startswith("."):
            continue
        if path.name in IGNORE_NAMES:
            continue
        if path.is_file():
            files.append(path)
    return files


def next_jane_message_path(subject: str) -> Path:
    dt = now_local()
    base = f"{dt.strftime('%Y-%m-%d-%H-%M')}-{slugify(subject, 40)}"
    candidate = JANE_INBOX / f"{base}.json"
    idx = 1
    while candidate.exists():
        candidate = JANE_INBOX / f"{base}-{idx}.json"
        idx += 1
    return candidate


def write_jane_message(run_id: str, title: str, packet_path: Path, source_path: Path) -> Path:
    dt = now_local()
    subject = f"Agent Bus: Research Ingested - {title}"
    content = (
        f"run_id: {run_id}\n"
        "flow: research -> plan(back and forth with Jane) -> atomic task list -> subagents execute\n"
        "next_step: draft plan markdown with checklist bullets and run plan expansion"
    )
    payload = {
        "_meta": {
            "from": "codex-cli",
            "to": "claude-code",
            "date": dt.strftime("%Y-%m-%d"),
            "timestamp": dt.strftime("%H:%M"),
            "type": "task-proposal",
            "status": "unread",
            "processing": {},
        },
        "subject": subject,
        "content": content,
        "attachments": [str(packet_path), str(source_path)],
        "in_reply_to": None,
    }
    path = next_jane_message_path(subject)
    write_json(path, payload)
    return path


def ingest_file(path: Path) -> tuple[str, Path, Path]:
    dt = now_local()
    title = path.stem
    run_id = f"ABUS-{dt.strftime('%Y%m%d-%H%M%S')}-{slugify(title, 24)}"
    text = path.read_text(encoding="utf-8", errors="replace")
    packet = {
        "type": "research",
        "run_id": run_id,
        "status": "queued",
        "created_at": now_iso(),
        "from_agent": "codex-cli",
        "title": title,
        "source_path": str(path),
        "source_excerpt": text[:1800],
        "next_step": "plan_back_and_forth_with_jane",
    }
    packet_path = BUS_INBOX / f"{run_id}.research.json"
    write_json(packet_path, packet)
    message_path = write_jane_message(run_id, title, packet_path, path)
    return run_id, packet_path, message_path


def main() -> int:
    ensure_dirs()
    state = load_state()
    all_files = list_obsidian_files()
    all_names = [p.name for p in all_files]

    if not state.get("bootstrapped"):
        state["bootstrapped"] = True
        state["known_files"] = all_names
        state["last_ingested_count"] = 0
        save_state(state)
        log_line(f"bootstrap known_files={len(all_names)}")
        return 0

    known = set(state.get("known_files", []))
    current = {p.name: p for p in all_files}
    new_names = sorted(set(current) - known)

    ingested = 0
    for name in new_names:
        src = current[name]
        run_id, packet_path, message_path = ingest_file(src)
        ingested += 1
        log_line(
            "ingested "
            f"source={src.name} run_id={run_id} "
            f"packet={packet_path.name} message={message_path.name}"
        )

    state["known_files"] = all_names
    state["last_ingested_count"] = ingested
    save_state(state)
    log_line(f"scan complete new={len(new_names)} ingested={ingested}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
