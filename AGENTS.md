---
title: IVCO Codex Runtime Router
status: ACTIVE
version: 2026-05-12.1
date: 2026-05-12
owner: macmini codex-cli Chi
canonical_path: projects/ivco/AGENTS.md
mirror: obsidian/projects/ivco/root/AGENTS.md
project: ivco
---

# IVCO — Intelligent Valuation Confidence Observatory

> Integrating Graham, Buffett, Fisher, Munger into an AI-native value investing research engine.

## Quick Reference

| Item | Value |
|------|-------|
| **Status** | v0.2.0 Released — Phase 0.5a Complete |
| **DNA** | `docs/ivco-dna.md` (project soul document) |
| **Allen Framework** | `~/fisher/projects/ivco/allen-framework-tsmc-owners-earning.md` |
| **GitHub** | ConversionCrafter/allen-ivco |
| **Domains** | ivco.io (primary) + ivco.ai (defense) |
| **Brand** | IVCO Fisher (@ivco_fisher) — public persona |
| **Codex Governance** | `docs/governance/codex-session-governance.md` |
| **Cross-Project Index** | `~/fisher/projects/allen-ai-os/docs/ivco-context-index.md` |

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

## Codex Session Governance

Read `docs/governance/codex-session-governance.md` before Codex session,
handoff, document-governance, or cross-agent work in this repo.

Canonical session commands are global Codex skills:

- `$sc`: resume the global Codex lane and active handoff.
- `$ss`: write a checkpoint handoff while keeping the Codex lane active.
- `$save`: write the final handoff and close the Codex lane.

Do not create project-local copies of these skills. IVCO-specific work is
referenced from the global Codex handoff via this repo's task, plan, and
governance files.

## Team & Communication

**Constitution**: Read `~/fisher/shared-state/team-dna/constitution.md` when
the task touches shared agent principles.

| Agent | Runtime | Owned Surface | Role |
|-------|---------|---------------|------|
| **Chi** | Codex CLI | `AGENTS.md`, Codex skills, Codex handoffs, Codex-owned tasks | Engineering executor, review, verification |
| **Jane** | Claude Code | `CLAUDE.md`, `.claude/**`, Claude-owned handoffs | Project orchestration and Claude runtime governance |
| **Hermes** | Hermes agent | `.hermes.md`, Hermes memory/runtime files | Hermes runtime governance |
| **Kiro** | Kiro CLI | `docs/plans/kiro/**` | Kiro runtime handoffs and steering |
| **Show** | Claude Desktop / Show lane | shared analysis and governance surfaces assigned by Allen | Strategy, critique, governance review |
| **Fisher** | public persona | public-facing IVCO voice | American English brand voice |

Cross-runtime suggestions travel through `agent-talk-3round` and shared
canonical files. In cmux-hosted collaboration, use a notice-only `cmux send`
pointer plus `cmux send-key Enter`; keep payloads in shared JSONL transport,
not terminal text.

## Blog Content (7 articles ready, pending Payload deploy)

All articles written in English, Fisher's voice. Topics: Allen Framework, TSMC Case Study, Owner Earnings, Why IVCO, Three-Stage DCF, Confidence Coefficient, How IVCO Became an Intelligence.

## Session Start

For Codex sessions opened from `projects/ivco/`:

1. Use `$sc` when Allen asks to resume or continue the Codex lane.
2. Read `docs/governance/codex-session-governance.md` for IVCO-specific Codex
   session rules.
3. Read `~/fisher/projects/allen-ai-os/docs/ivco-context-index.md` for current
   IVCO status before broad project work.
4. Load only the task-specific IVCO docs needed for the active change.

Load deeper context on demand:
- **L0**: this router + Codex session-governance doc.
- **L1**: cross-project IVCO context index.
- **L2**: domain docs such as `docs/ivco-dna.md`,
  `allen-framework-tsmc-owners-earning.md`, and `docs/expert-manual-v2.md`.
- **L3**: historical plans, reviews, archives, and raw evidence.

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

## Document Governance

Before creating or modifying durable Markdown, follow local-first plus
same-transaction Obsidian symlink mirror:

1. Read `~/fisher/projects/allen-ai-os/docs/governance/document-governance-index.md`.
2. Read `~/fisher/projects/allen-ai-os/docs/governance/document-write-policy.md`.
3. For document-family work, read
   `~/fisher/projects/allen-ai-os/docs/governance/context-entropy-management-governance.md`.
4. Use the IVCO mappings in `docs/governance/codex-session-governance.md`.
5. Never write durable Markdown directly under `obsidian/`.

## Self-Improvement Protocol

After a correction from Allen or a verified repeated defect:

1. Record the durable pattern in the canonical Codex/shared improvement surface
   required by the active skill or workflow.
2. Use debug-log artifacts for defects when the active workflow requires them.
3. If the finding affects a peer runtime, send a bounded `agent-talk-3round`
   suggestion instead of editing that runtime's private files.

## Development Rules

### Research-First Workflow
1. **Research existing code first** — read the files you're about to change before making changes
2. **Plan your approach** — identify scope, risk areas, test coverage gaps
3. **Execute with verification** — atomic changes, verify after each step
4. **Test before reporting** — run tests and include evidence in your report
5. **Record lessons** — write durable lessons only to the active workflow's
   canonical improvement surface.

### Collaboration Strategy

- Keep Codex critical-path work local when the next step depends on it.
- Use Codex subagents only when the active runtime contract allows it and the
  delegated slice has a bounded, non-overlapping scope.
- Use `agent-talk-3round` for peer LLM collaboration and runtime-boundary
  suggestions.
- Do not edit `.claude/**`, `.hermes.md`, or `docs/plans/kiro/**` from Codex
  unless Allen explicitly delegates that cross-runtime maintenance task.

### Code Standards
- Conventional Commits: `fix/feat/refactor/docs/test/chore`
- Atomic commits: one thing per commit
- Python CLI tools prefixed `ivco-*`
- Tests required for feature changes
- Read `CLAUDE.md` in this directory for full detail (Jane's authoritative version)
