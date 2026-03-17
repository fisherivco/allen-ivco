# IVCO: The Allen Framework for Intelligent Valuation

> World's first intelligent value investing observatory integrating Graham, Buffett, Fisher, and Munger

## Project Overview

| Item | Value |
|------|-------|
| **Name** | IVCO (Intrinsic Value Confidence Observatory) |
| **Brand** | IVCO Fisher (@ivco_fisher) |
| **Status** | Phase 0.5 Content & Launch (MVP V0 merged, Blog drafts ready) |
| **Created** | 2026-01-31 |
| **Path** | `/Users/allenchenmac/fisher/projects/allen-ivco/` |
| **GitHub** | ConversionCrafter/allen-ivco |
| **Domains** | ivco.io (primary) + ivco.ai (defense) |

## Tech Stack

| Category | Technology |
|----------|-----------|
| CMS | Payload CMS + Next.js |
| Database | Supabase (PostgreSQL) + Qdrant (Vector) |
| CLI | Python 3.10+ / Click |
| Automation | n8n |
| AI | Claude Code + MCP Servers |

## Architecture

```
Three-Layer Architecture:
  Layer 1: IVC Framework (Immutable)     — Philosophy + Core Formula
  Layer 2: IVC Perception (Extensible)   — Python CLI + Watchers + n8n
  Layer 3: IVC Judgment (Human Only)     — CC adjustment + Buy/Hold/Sell

Tech Stack:
  Presentation:  Payload CMS + Next.js Frontend
  Application:   Python CLI Tools + n8n Automation
  Data:          Supabase (Relational) + Qdrant (Vector Search)
  Integration:   MCP Servers + Claude Skills + Claude Code
```

## Commands

```bash
# Docker (local dev)
docker compose up -d          # Start DB + CMS + n8n
docker compose down           # Stop all services
docker compose logs app -f    # CMS logs

# Python CLI — ivco-calc (three-tier calibration + three-stage DCF)
cd cli/ivco-calc
pip3 install -e ".[dev]"
ivco calc-oe --ticker TSMC    # Calculate Owner Earnings
ivco calc-iv --ticker TSMC    # Calculate Intrinsic Value (DCF)
ivco analyze --ticker TSMC    # Full pipeline

# Python CLI — ivco-filter (stock screening)
cd cli/ivco-filter
pip3 install -e .
ivco-filter run               # Run filter rules

# Tests (57 tests)
cd cli/ivco-calc && python3 -m pytest tests/ -v
cd cli/ivco-filter && python3 -m pytest tests/ -v

# Supabase (production)
# Must use Session Pooler: aws-0-ap-northeast-1.pooler.supabase.com:5432
# Direct Connection (db.*.supabase.co) is IPv6 only — incompatible with Taiwan ISPs
# Full guide: docs/supabase-action-guide.md

# Git
git status && git log --oneline -5
```

## Core Formula: Three-Tier Calibration + Three-Stage DCF

```
Three-Tier Calibration Pipeline:
  Layer 1: OE_calibrated = OE x Reality_Coefficient
  Layer 2: CAGR = f(OE_calibrated)
  Layer 3: CAGR_adjusted = CAGR x Confidence_Coefficient

IV_per_share = (DCF_Sum - Long_Term_Debt) / Shares_Outstanding

Stage 1 (Years 1-5):  CAGR_adjusted (Historical OE CAGR x CC)
Stage 2 (Years 6-10): CAGR_moderate  (company-specific conservative)
Stage 3 (Perpetuity):  g_perpetual   (company-specific perpetual growth)
Discount rate r = US 10-Year Treasury Yield + ~3% inflation premium
```

**TSMC Reference** (calibrated 2026-02-13): IV Range = NT$4,565 ~ NT$5,639/share.
Full methodology: `allen-framework-tsmc-owners-earning.md`

## Key Concepts

| Concept | Definition |
|---------|-----------|
| **Owner Earnings** | Net Income + D&A - Maintenance CapEx - Working Capital Changes |
| **Reality Coefficient** | Corrects historical OE distortions (100% = accurate, >100% = understated, <100% = overstated) |
| **Confidence Coefficient** | Multiplies CAGR: Conservative 0.8-1.0x / Steady 1.0-1.5x / Aggressive 1.5-2.5x / Extreme 2.5x+ / Integrity stain = Terminate |
| **Biological Moat** | Decades of precise execution (stable gene) vs CEO/strategy pivot (mutation risk) |

## File Structure

```
allen-ivco/
├── CLAUDE.md               # Project memory (this file)
├── AGENTS.md               # Agent roles and workflow
├── TODO.md                 # Task tracking
├── PROGRESS.md             # Milestone progress
├── cli/
│   ├── ivco-calc/          # OE/IV calculation engine (v0.3.0, 57 tests)
│   │   ├── ivco_calc/      # Source: cli.py, cagr.py, dcf.py, store.py, verify.py
│   │   └── tests/          # 13 test files
│   └── ivco-filter/        # Stock screening rules engine
│       ├── ivco_filter/    # Source: cli.py, rules.py, scorer.py, lists.py
│       └── tests/
├── cms/                    # Payload CMS configuration
├── docs/                   # Documentation
│   ├── ivco-dna.md         # Project soul document (863 lines, 21 sources)
│   └── supabase-action-guide.md
├── schemas/                # Data schemas
├── scripts/                # Utility scripts
├── docker-compose.yml      # Local: PostgreSQL 15 + Node 22 + n8n
└── .env.docker             # Docker environment
```

## Key Files

| File | Purpose |
|------|---------|
| `docs/ivco-dna.md` | Project DNA — distilled from 21 research sources (863 lines) |
| `allen-framework-tsmc-owners-earning.md` | TSMC calculation reference (Allen's actual methodology) |
| `AGENTS.md` | Agent roles, workflow, system prompts (Jane + Chi) |
| `cli/ivco-calc/ivco_calc/cli.py` | Main CLI entry point (Click) |
| `cli/ivco-calc/ivco_calc/dcf.py` | Three-stage DCF engine |
| `cli/ivco-calc/ivco_calc/store.py` | Supabase storage layer |
| `docs/supabase-action-guide.md` | Supabase connection strategy + setup |
| `docker-compose.yml` | Local dev: PG15 (:5433) + CMS (:3000) + n8n (:5678) |
| `docs/upgrade-backlog.md` | Accumulated upgrade requirements — read first when planning next version |

## Supabase Connection Rules

| Environment | DATABASE_URL |
|-------------|-------------|
| Dev (Docker) | `postgresql://ivco_user:ivco_password@localhost:5433/ivco_dev` |
| Dev (inside container) | `postgresql://ivco_user:ivco_password@db:5432/ivco_dev` |
| Prod (Supabase) | Session Pooler `aws-0-*.pooler.supabase.com:5432` (IPv4) |

- Region: Tokyo (ap-northeast-1) — 47ms from Taiwan
- Pooler username format: `postgres.[PROJECT_REF]`
- Transaction Mode (port 6543): Not recommended for Payload (prepared statement issues)
- Free Plan: DB auto-pauses after 7 days; Pro Plan ($25/month) for production

## Team Roles (Lobster Architecture)

> Full architecture: `~/.claude/CLAUDE.md` § Lobster Architecture

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Allen** | Human | IVC Framework owner, CC judgment, Buy/Hold/Sell decisions |
| **Jane** (Brain) | Claude Opus | Orchestrator — risk gatekeeper, analysis direction, final acceptance |
| **Chi** (Claws) | Claude (Sonnet/Opus) | Sonnet: logistics, packaging. Opus: independent B-Test, code review |
| **Jack** (Claws) | GPT (Codex CLI) | A-Build executor — production code, self-verify, plan challenge |

Agent definitions: `~/.claude/agents/jane.md`, `~/.claude/agents/chi.md`
Project-specific roles: `AGENTS.md`

## IVCO-Specific Gotchas

- **Supabase IPv4 only**: Taiwan ISPs don't support IPv6. Always use Session Pooler (`pooler.supabase.com:5432`), never Direct Connection (`db.*.supabase.co`)
- **Three-stage DCF, not two**: Stage 1 (years 1-5, CAGR_adjusted), Stage 2 (years 6-10, decelerating), Stage 3 (perpetuity). Never simplify to two-stage
- **CC is human-only**: Confidence Coefficient adjustment is Allen's exclusive judgment. CLI provides data, never auto-applies CC
- **Owner Earnings formula**: Must use Maintenance CapEx (not total CapEx). Allen's framework explicitly separates growth vs maintenance spending
- **Docker port**: PostgreSQL on `:5433` (not default `:5432`) to avoid conflicts with system PostgreSQL

> Workflow Orchestration (§1-§6), Task Management, Core Principles, and Pipeline are defined in `~/.claude/CLAUDE.md` (auto-loaded globally). Not duplicated here.

## Milestones

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Framework definition + team roles | Complete |
| Phase 0.5 | Content & Launch (MVP V0 + Blog drafts) | In Progress |
| Phase 1 | Payload CMS data architecture (7 Collections) | 40% (1/7) |
| Phase 2 | Python CLI (ivco-calc v0.3.0 merged, ivco-filter built) | 60% |
| Phase 3 | n8n automation pipeline | Planned |
| Phase 4 | Frontend interface | Planned |
| Phase 5 | Vector search (Qdrant) | Planned |

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-31 | Three-layer architecture | Framework (immutable) + Perception (extensible) + Judgment (human only) |
| 2026-02-04 | Supabase (PostgreSQL) | Relational fit, Realtime, RLS, query performance |
| 2026-02-04 | Per-share value output mandatory | Prevents "evaluating only by total market cap" error |
| 2026-02-09 | Brand unified as IVCO | IVC Calculator -> IVCO (Observatory). Fisher as brand persona |
| 2026-02-09 | Domains: ivco.io + ivco.ai | Primary + defensive acquisition |
| 2026-02-13 | TSMC calibration validated | Three-tier + Three-stage DCF verified against Allen's actual calculation |

## References

- Workspace rules: `/Users/allenchenmac/fisher/CLAUDE.md`
- Project index: `/Users/allenchenmac/fisher/memory/projects/project-index.json`
- IVCO pre-work task: `fisher/obsidian/task/ivco-pre-work-infrastructure.md`
