---
title: Kiro Agent Talk Handshake Checklist
status: COMPLETE
version: 2026-05-12.1
date: 2026-05-12
owner: macmini codex-cli Chi
canonical_path: projects/ivco/tasks/kiro-agent-talk-handshake-20260512-checklist.md
mirror: obsidian/projects/ivco/tasks/kiro-agent-talk-handshake-20260512-checklist.md
project: ivco
---

# Kiro Agent Talk Handshake Checklist

## Acceptance Checks

- [x] Read `agent-talk-3round` protocol and cmux wake-plane references.
- [x] Verify Chi skill availability from `projects/ivco/`.
- [x] Inspect cmux topology with `cmux tree --all`.
- [x] Read candidate surfaces before selecting Kiro.
- [x] Confirm not to target Claude Code Show, Hermes, or Chi.
- [x] Append Round 0 packet to `kiro.jsonl`.
- [x] Send one-line cmux pointer to Kiro with `cmux send`.
- [x] Submit the pointer with `cmux send-key Enter`.
- [x] Receive same-thread Kiro reply in `chi.jsonl`.
- [x] Record Kiro's result: pass, partial, or blocker.
- [x] Run thread cleanup helper.
- [x] Report exact evidence to Allen.

## Verification Commands

```bash
cmux tree --all
cmux read-screen --workspace <workspace> --surface <surface> --scrollback --lines 20
/Users/fisherivco/fisher/projects/allen-ai-os/.codex/skills/agent-talk-3round/scripts/agent-talk-wait.sh --self chi --thread <thread_id> --from kiro --role builder --builder chi --reviewer kiro --timeout 600
```

## Traceability

- Goal: `tasks/kiro-agent-talk-handshake-20260512-goal.md`.
