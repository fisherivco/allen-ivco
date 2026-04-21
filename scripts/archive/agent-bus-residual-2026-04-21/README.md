# Archived: Agent Bus Residual Workers — 2026-04-21

## Why Archived

Agent Bus was frozen 2026-03-31 and fully purged 2026-04-21 (S223–S225).
These two worker scripts hardwire paths into the now-deleted agent-bus repo
and cannot function. Archiving preserves forensic history without polluting
the active scripts directory.

Reference: `projects/allen-ai-os/docs/handoffs/agent-bus-purge-2026-04-21.md`

## Archived Files

### agent_bus_executor_worker.py
- **Original path**: `projects/ivco/scripts/agent_bus_executor_worker.py`
- **Dead hardwired paths**:
  - `~/fisher/projects/agent-bus/scripts/agent-bus-flow.py` (PURGED)
  - `~/fisher/shared-state/agent-bus/` (PURGED)
  - `~/fisher/shared-state/contributions/codex/logs/agent-bus-executor.log`
- **Function**: Single-pass launchd worker that claimed + executed command tasks
  from the Agent Bus via `agent-bus-flow.py`. Fully inoperable without the Bus.

### agent_bus_ingest_worker.py
- **Original path**: `projects/ivco/scripts/agent_bus_ingest_worker.py`
- **Dead hardwired paths**:
  - `~/fisher/shared-state/agent-bus/inbox/` (PURGED)
  - `~/fisher/shared-state/agent-bus/status/` (PURGED)
  - `~/fisher/shared-state/contributions/codex/logs/agent-bus-ingest-worker.log`
- **Function**: Single-pass launchd worker that ingested new Obsidian inbox notes
  into the Agent Bus task queue. The valid JANE_INBOX path
  (`~/fisher/shared-state/inbox/claude-code`) still exists but the Bus
  write target (`BUS_INBOX`) is gone.

## Status

**OBSOLETE — do not restore.**

The Agent Bus protocol is superseded by inbox JSON packets per
`{project}/inbox/PROTOCOL.md` + codex-companion MCP.
Any replacement for these workers must be built against the new protocol.

## Archived Date

2026-04-21 (S225 Agent Bus purge cleanup)

---

### codex_inbox_watcher.py

- **Original path**: `projects/ivco/scripts/codex_inbox_watcher.py`
- **Invoked by**: `projects/ivco/watch` shell script (also deleted 2026-04-21)
- **Function**: Detected unread inbox messages, wrote `.inbox-digest.json` + trigger metadata for Jack's startup consumption. Also referenced a launchd worker (`com.allen.codex-inbox-worker`).
- **Dead dependency**: The inbox paths it scanned and the launchd worker infrastructure are all part of the purged Agent Bus ecosystem.
- **AGENTS.md reference**: Line documenting `python3 ~/fisher/projects/allen-ivco/scripts/codex_inbox_watcher.py` was removed from the Inbox Watcher Protocol section.
- **Why archived (not deleted)**: Forensic preservation per S225 cleanup policy. Archived via `git mv` to preserve history.
- **Verdict**: OBSOLETE — do not restore. Inbox scanning is now handled by inbox JSON packet glob pattern per `shared-state/inbox/PROTOCOL.md`.
