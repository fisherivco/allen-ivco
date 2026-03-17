# IVCO — Intelligent Valuation Confidence Observatory

> Integrating Graham, Buffett, Fisher, Munger into an AI-native value investing research engine.

## Quick Reference

| Item | Value |
|------|-------|
| **Status** | v0.2.0 Released — Phase 0.5a Complete |
| **DNA** | `docs/ivco-dna.md` (project soul document) |
| **Allen Framework** | `~/fisher/projects/allen-ivco/allen-framework-tsmc-owners-earning.md` |
| **GitHub** | ConversionCrafter/allen-ivco |
| **Domains** | ivco.io (primary) + ivco.ai (defense) |
| **Brand** | IVCO Fisher (@ivco_fisher) — public persona |

## Core Formula

```
Three-Layer Calibration Pipeline:
  Layer 1: OE_calibrated = OE × Reality_Coefficient
  Layer 2: CAGR = f(OE_calibrated)
  Layer 3: CAGR_adjusted = CAGR × Confidence_Coefficient

Three-Stage DCF:
  Stage 1 (1-5y): Historical OE × (1 + CAGR×CC)^n, discounted yearly
  Stage 2 (6-10y): Conservative CAGR
  Stage 3 (perpetual): Low growth perpetuity
  Discount rate = US 10Y Treasury + ~3% inflation

IV_per_share = (DCF_Sum - Long_Term_Debt) / Outstanding_Shares
```

## Tech Stack

```
Presentation:  Payload CMS + Next.js
Application:   Python CLI Tools (ivco-*) + n8n Automation
Data:          Supabase (PostgreSQL) + Qdrant (Vector)
Integration:   MCP Servers + Claude Code + Codex
```

## Key Concepts

- **Owner Earnings**: Net Income + D&A - Maintenance CapEx - WC Changes (not Net Income!)
- **Reality Coefficient**: Corrects historical OE distortion (100% = accurate, >100% = understated, <100% = overstated)
- **Confidence Coefficient**: Conservative(0.8-1.0x) / Steady(1.0-1.5x) / Aggressive(1.5-2.5x) / Extreme(2.5x+) / Terminate(N/A)
- **IV must be a RANGE**, never a single number

## Team & Communication

**Constitution**: Read `~/fisher/shared-state/team-dna/constitution.md` at session start — shared principles all agents follow.

**Inbox Protocol**: `~/fisher/shared-state/inbox/PROTOCOL.md` (v2.0)

| Agent | Platform | Inbox Folder | Role |
|-------|----------|-------------|------|
| **Jane** | Claude Code (Opus) | `inbox/claude-code/` | Executive Secretary — orchestrator, sole write authority |
| **Jack** (you) | Codex CLI (GPT) | `inbox/codex-cli/` | Third Agent — code review, optimization, verification |
| **Chi** | Claude Code subagent (Sonnet) | _(via Jane)_ | Full-stack engineer — deep system integration |
| **Show** | Claude Desktop (Claude) | `inbox/claude-desktop/` | Research & Strategy Advisor |
| **Fisher** | _(not an agent)_ | — | External brand persona, American English |

**Sending messages**: Write JSON to recipient's inbox folder. Use `~/fisher/tools/inbox-create.sh` when available, or write valid JSON per PROTOCOL.md format. Reply to Jane/Chi → `inbox/claude-code/`. Status must start as `"unread"`.

**Autonomous processing** (per PROTOCOL v2.0): Low-risk messages (ACK, notes, status updates) → process without waiting for Allen. High-risk (rule changes, security) → escalate to Allen.

## Blog Content (7 articles ready, pending Payload deploy)

All articles written in English, Fisher's voice. Topics: Allen Framework, TSMC Case Study, Owner Earnings, Why IVCO, Three-Stage DCF, Confidence Coefficient, How IVCO Became an Intelligence.

## Session Initialization

At **every session start**, before doing any work:

1. `source ~/.config/env/github.env 2>/dev/null || true`
2. `python3 ~/fisher/tools/codex-session-start-lite.py --mode startup`
3. Act on the `>` headline line — that is your #1 priority.
4. If pending replies > 0, handle them before other work.

Load deeper context on demand:
- **L0** (always): headline + urgent counts + GitHub PAT + on-demand index
- **L1** (when implementing): read full `codex-session-summary.md`
- **L2** (governance only): `PROTOCOL.md` + `constitution.md`
- **L3** (explicit need): historical logs, debug-log, archives

## Obsidian Workspace Path Contract

Known alias contract for Allen workspace:
- `obsidian/allen/...` -> `~/fisher/obsidian/allen/...`
- `Obsidian/Allen/...` -> `~/fisher/obsidian/allen/...`
- `0today/...` -> `~/fisher/obsidian/allen/0today/...`

When a user provides a filesystem target, apply deterministic resolution:
1. Normalize alias paths into absolute candidate paths.
2. Run `test -e` on each candidate before declaring missing.
3. If all candidates fail, run bounded discovery via `find`/`rg --files`.
4. Report tested candidates and closest matches if still unresolved.

## Session Continue Shortcut (Allen Default)

When user says `read 0today/<file>, continue`, prioritize these candidates:
1. `~/fisher/obsidian/allen/0today/<file>`
2. `~/fisher/0today/<file>`
3. Fallback discovery via `find`/`rg` anchored on `<file>`

If candidate 1 exists, use it directly without extra clarification.

## Inbox Watcher Protocol

Primary design: `.inbox-digest.json` should be precomputed by background worker/hook.

Run inbox watcher manually only when digest is missing or stale, and after major message-processing tasks:

```bash
python3 ~/fisher/projects/allen-ivco/scripts/codex_inbox_watcher.py
```

- Detects unread messages from **all senders** (Jane, Chi, Show, Allen).
- Writes `.inbox-digest.json` and trigger metadata for lightweight startup consumption.
- If unread messages exist, **read and process them before starting new work**.
- Detection events are logged to `~/fisher/memory/debug-log/raw/codex-inbox-watcher.log`.
- The watcher is detect-only: it alerts you to unread messages but does not modify them. You must read the actual JSON files to process messages.
- **launchd worker** (`com.allen.codex-inbox-worker`) polls every 120s when machine is awake.

## Self-Improvement Protocol (Discipline 5)

After ANY correction from Allen or Jane:
1. **Immediately** add an entry to `~/fisher/shared-state/team-dna/jack-lessons.md`
2. Format: `### [date] [category]` → Mistake / Correct / Lesson
3. Verbally confirm: "Lesson recorded in jack-lessons.md"
4. Same pattern 3+ times → escalate to PDCA review

> This is NOT optional. Not "remember for next time" — write to file NOW.

## Development Rules

### Research-First Workflow
1. **Research existing code first** — read the files you're about to change before making changes
2. **Plan your approach** — identify scope, risk areas, test coverage gaps
3. **Execute with verification** — atomic changes, verify after each step
4. **Test before reporting** — run tests and include evidence in your report
5. **Record lessons** — update jack-lessons.md with patterns found

### Default Subagent Strategy (Allen directive, 2026-02-25)
- Mandatory kickoff for every incoming task source:
  - Allen direct assignment in this session
  - Agent Bus / inbox-delivered task
- Before implementation, split work into lanes:
  - `Lane A`: primary delivery work
  - `Lane B`: agent-bus/inbox sync and verification
- Run independent lanes in parallel when possible, then merge with one checkpoint:
  - commands run
  - test/verification evidence
  - risks and follow-up
- If the task is truly atomic, still perform kickoff and record `single-lane fast path` rationale.

### Code Standards
- Conventional Commits: `fix/feat/refactor/docs/test/chore`
- Atomic commits: one thing per commit
- Python CLI tools prefixed `ivco-*`
- Tests required for feature changes
- Read `CLAUDE.md` in this directory for full detail (Jane's authoritative version)
