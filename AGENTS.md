# IVCO — Intelligent Valuation Confidence Observatory

> Integrating Graham, Buffett, Fisher, Munger into an AI-native value investing research engine.

## Quick Reference

| Item | Value |
|------|-------|
| **Status** | v0.2.0 Released — Phase 0.5a Complete |
| **DNA** | `docs/ivco-dna.md` (project soul document) |
| **Allen Framework** | `allen-framework-tsmc-owners-earning.md` (top-level methodology) |
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

## Team Roles in IVCO

- **Jane**: Devil's Advocate + engineering orchestrator. Challenges every investment thesis.
- **Chi**: Full-stack engineer persona. Implements features.
- **Fisher**: External brand persona (not an agent). American English, targets English-speaking value investors.

## Blog Content (7 articles ready, pending Payload deploy)

All articles written in English, Fisher's voice. Topics: Allen Framework, TSMC Case Study, Owner Earnings, Why IVCO, Three-Stage DCF, Confidence Coefficient, How IVCO Became an Intelligence.

## Inbox Watcher Protocol

At **session start** and **after completing each major task**, run:

```bash
python3 ~/AI-Workspace/projects/allen-ivco/scripts/codex_inbox_watcher.py
```

- If unread messages exist, **read and process them before starting new work**.
- If zero unread, the script exits silently (no action needed).
- Detection events are logged to `~/AI-Workspace/memory/debug-log/raw/codex-inbox-watcher.log`.
- The watcher is detect-only: it alerts you to unread messages but does not modify them. You must read the actual JSON files to process messages.

This is the Codex-side counterpart to Jane's automatic PostToolUse hook. Following this protocol ensures messages from Chi/Jane are never missed.

## Development Rules

- Conventional Commits: `fix/feat/refactor/docs/test/chore`
- Atomic commits: one thing per commit
- Python CLI tools prefixed `ivco-*`
- Tests required for feature changes
- Read `CLAUDE.md` in this directory for full detail (Jane's authoritative version)
