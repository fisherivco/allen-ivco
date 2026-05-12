---
title: Kiro Agent Talk Handshake Goal
status: COMPLETE
version: 2026-05-12.1
date: 2026-05-12
owner: macmini codex-cli Chi
canonical_path: projects/ivco/tasks/kiro-agent-talk-handshake-20260512-goal.md
mirror: obsidian/projects/ivco/tasks/kiro-agent-talk-handshake-20260512-goal.md
project: ivco
---

# Kiro Agent Talk Handshake Goal

## Goal

Verify that `macmini codex-cli Chi` and `kiro-cli` can coordinate from
`projects/ivco/` using the `agent-talk-3round` skill, JSONL transport, and the
cmux notice-only wake plane.

## Scope

- Chi is the initiator and builder/driver.
- Kiro is the receiver and reviewer/tester.
- Use `shared-state/inbox/transport/kiro.jsonl` as Kiro's inbound payload
  plane and `shared-state/inbox/transport/chi.jsonl` as Chi's reply plane.
- Use `cmux send` plus `cmux send-key Enter` only for a one-line pointer.
- Confirm the live cmux topology before sending anything to Kiro.

## Anti-Goals

- Do not send rich task content through cmux.
- Do not mutate Kiro private runtime state.
- Do not involve Claude Code Show or Hermes except as topology surfaces to
  avoid.
- Do not commit or push unless Allen separately delegates closure.

## Success Criteria

- [x] Current cmux surfaces are identified and Kiro's surface is selected by
  evidence, not assumption.
- [x] Round 0 packet is appended to Kiro's JSONL inbox with top-level/body
  `thread_id` parity.
- [x] Kiro is woken with a single-line cmux notice and `cmux send-key Enter`.
- [x] Kiro replies on the same thread to Chi's JSONL inbox.
- [x] The reply confirms Kiro can use or invoke its `agent-talk-3round` skill path
  from `projects/ivco/`, or reports a concrete blocker.
- [x] Chi verifies its own `agent-talk-3round` skill availability from
  `projects/ivco/`.
- [x] Cleanup helper is run for the thread before reporting closure.

## Outcome

`KIRO_AGENT_TALK_HANDSHAKE_COMPLETE`.

Evidence:

- Kiro target: `workspace:2 surface:5`, Kiro CLI, cwd `~/fisher/projects/ivco`.
- Chi skill check: `STRUCTURE_OK` for the Codex `agent-talk-3round` skill from
  `projects/ivco/`.
- Kiro reply: `kiro-1778592493004` in `chi.jsonl`.
- Close packet: `chi-1778592541406` in `kiro.jsonl`.
- Cleanup: `AGENT_TALK_CLEANUP_OK`.

## Traceability

- User request: `$agent-talk-3round initiator` Kiro handshake from
  `projects/ivco/`.
- Skill: `projects/allen-ai-os/.codex/skills/agent-talk-3round/SKILL.md`.
