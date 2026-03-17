#!/usr/bin/env python3
"""Agent Bus executor worker.

Single-pass worker intended for launchd StartInterval polling:
claim -> execute(command tasks) -> complete
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path.home() / "fisher"
FLOW_CLI = ROOT / "projects" / "agent-bus" / "scripts" / "agent-bus-flow.py"
LOG_FILE = ROOT / "shared-state" / "contributions" / "codex" / "logs" / "agent-bus-executor.log"
DEFAULT_ASSIGNEE = "codex-cli"
DEFAULT_WORKER = "codex-cli-1"
MAX_TEXT = 1200


def log(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{ts} {message}\n")


def run_flow(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["python3", str(FLOW_CLI)] + args,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def parse_claim_output(stdout: str) -> dict[str, str] | None:
    if not stdout or stdout == "no_claimable_task":
        return None
    try:
        data = json.loads(stdout)
        if isinstance(data, dict) and "claimed" in data and "task_file" in data:
            return {"claimed": str(data["claimed"]), "task_file": str(data["task_file"])}
    except json.JSONDecodeError:
        return None
    return None


def read_task(task_file: Path) -> dict[str, Any]:
    return json.loads(task_file.read_text(encoding="utf-8"))


def run_command(command: str, *, timeout: int, workdir: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        ["zsh", "-lc", command],
        cwd=str(workdir),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    merged = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    merged = merged.strip()
    if len(merged) > MAX_TEXT:
        merged = merged[:MAX_TEXT] + "...(truncated)"
    ok = proc.returncode == 0
    return ok, f"exit={proc.returncode} output={merged or '(empty)'}"


def complete_task(
    *,
    task_id: str,
    worker: str,
    status: str,
    summary: str,
    commands: list[str],
    evidence: list[str],
    risks: list[str],
    lessons: list[str],
) -> None:
    args = [
        "complete",
        "--task-id",
        task_id,
        "--worker",
        worker,
        "--status",
        status,
        "--summary",
        summary,
    ]
    for item in commands:
        args.extend(["--command", item])
    for item in evidence:
        args.extend(["--evidence", item])
    for item in risks:
        args.extend(["--risk", item])
    for item in lessons:
        args.extend(["--lesson", item])
    code, out, err = run_flow(args)
    if code != 0:
        log(f"complete_failed task_id={task_id} code={code} stderr={err}")
    else:
        log(f"complete_ok task_id={task_id} status={status} out={out}")


def handle_task(worker: str, task_file: Path) -> None:
    task = read_task(task_file)
    task_id = str(task.get("id", ""))
    execution = task.get("execution", {})
    commands = execution.get("commands", []) if isinstance(execution, dict) else []

    if not isinstance(commands, list) or not commands:
        complete_task(
            task_id=task_id,
            worker=worker,
            status="failed",
            summary="Task has no execution.commands; command executor skipped.",
            commands=[],
            evidence=["no execution.commands found"],
            risks=["task format mismatch for command executor"],
            lessons=["Add execution.commands for codex-exec assignee tasks."],
        )
        return

    timeout = 300
    workdir = ROOT
    if isinstance(execution, dict):
        # Accept both timeout_seconds (canonical) and timeout (legacy migration fallback)
        raw_timeout = execution.get("timeout_seconds") or execution.get("timeout", 300)
        if isinstance(raw_timeout, int) and raw_timeout > 0:
            timeout = int(raw_timeout)
        if isinstance(execution.get("workdir"), str) and execution["workdir"].strip():
            workdir = Path(execution["workdir"]).expanduser()

    cmd_records: list[str] = []
    evidence: list[str] = []
    for command in commands:
        command = str(command).strip()
        if not command:
            continue
        cmd_records.append(command)
        ok, output = run_command(command, timeout=timeout, workdir=workdir)
        evidence.append(output)
        if not ok:
            complete_task(
                task_id=task_id,
                worker=worker,
                status="failed",
                summary=f"Command failed: {command}",
                commands=cmd_records,
                evidence=evidence,
                risks=["non-zero exit code"],
                lessons=["Add preflight checks or smaller atomic commands."],
            )
            return

    complete_task(
        task_id=task_id,
        worker=worker,
        status="done",
        summary=f"Executed {len(cmd_records)} command(s) successfully.",
        commands=cmd_records,
        evidence=evidence,
        risks=["review command side effects before production usage"],
        lessons=["Command task execution succeeded with claim/lock isolation."],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Bus executor worker")
    parser.add_argument("--worker", default=os.environ.get("ABUS_WORKER_ID", DEFAULT_WORKER))
    parser.add_argument("--assignee", default=os.environ.get("ABUS_ASSIGNEE", DEFAULT_ASSIGNEE))
    args = parser.parse_args()

    # Hotfix-A: command executor must only claim execution tasks.
    code, stdout, stderr = run_flow(
        ["claim", "--worker", args.worker, "--assignee", args.assignee, "--task-kind", "execution"]
    )
    if code != 0:
        log(f"claim_failed worker={args.worker} code={code} stderr={stderr}")
        return code

    claim = parse_claim_output(stdout)
    if not claim:
        log(f"idle worker={args.worker} assignee={args.assignee}")
        return 0

    task_file = Path(claim["task_file"])
    if not task_file.is_file():
        log(f"claimed_task_missing worker={args.worker} task_file={task_file}")
        return 1

    log(f"claimed worker={args.worker} task_id={claim['claimed']}")
    handle_task(args.worker, task_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
