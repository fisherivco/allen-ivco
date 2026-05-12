---
title: S263 Checkpoint — ivco CEM Renovation + Path Y global-skill install staged, P0 closed
status: ACTIVE
schema_version: HANDOFF-SCHEMA-2.1.0
version: 2026-05-12.1
owner: macmini claude-code Show
canonical_path: projects/ivco/docs/plans/claude/handoffs/2026-05-12-claude-s263-checkpoint.md
mirror: obsidian/projects/ivco/handoffs/claude/2026-05-12-claude-s263-checkpoint.md
date: 2026-05-12
time: "2130"
timezone: Asia/Taipei
session: S263
type: checkpoint
machine: macmini
lane: claude
llm_model: claude-sonnet-4-6
session_id: S263-ivco-checkpoint
prior: null
related:
  - projects/allen-ai-os/docs/plans/agent-talk-3round-global-install-2026-05-12-goal.md
  - projects/allen-ai-os/docs/plans/agent-talk-3round-global-install-2026-05-12-checklist.md
  - projects/allen-ai-os/docs/plans/ivco-doc-architecture-renovation-2026-05-12-goal.md
  - projects/allen-ai-os/docs/plans/ivco-doc-architecture-renovation-2026-05-12-checklist.md
  - projects/allen-ai-os/docs/plans/show-skill-surface-inventory-2026-05-12.md
---

# S263 Checkpoint — ivco CEM Renovation + Path Y global-skill install staged, P0 closed

## Summary

S263 from the ivco/ cwd. Four workstreams executed:

**Path X (SHIPPED):** cmux wake-plane prefix bug fixed — SKILL.md v1.7.2 inline §Per-Runtime Trigger-Prefix Gate committed+pushed (allen-ai-os@24fe949). Show now validates trigger prefix before sending; Codex no longer rejects Show wakes from wrong surface.

**Path Y W2 (STAGED, awaiting D10.2 review):** Global agent-talk-3round install complete. SKILL.md v1.7.3 (gstack-pattern script paths) + Hermes upstream v1.3.0 (prefix rule parity) + `~/.claude/skills/agent-talk-3round/` 4-file symlink install verified (SHA-256 match, helper exec from /tmp exit 0). NOT YET COMMITTED — D10.2 adversarial Codex review required first (W3 gate), then commit (W4).

**ivco doc renovation W1-W2 (PLANNED):** Full audit of 33 in-scope ivco MD files complete. 23 Show-owned, 10 SKIP (cross-agent). 0 symlink mirrors, 0 CEM frontmatter. 8-wave renovation plan (W3-W10) drafted. W3 execute ready pending Allen W2→W3 checkpoint. Goal + checklist + W1 audit + W2 plan all committed to allen-ai-os.

**P0 Security (CLOSED):** Supabase DSN `postgresql://postgres:KU23MCfCAuQOb8kS@...` was in public git since 2026-02-06. DB password rotated (Allen, dashboard). New credential stored in `~/.config/env/supabase.env` as `SUPABASE_DB_PASSWORD_GACTTXNL`. TODO.md line 101 redacted → `psql "$DATABASE_URL"`. Committed ivco@31ff654 + pushed. Observation row appended.

**Also:** Global skill surface inventory completed — 29 Show skills audited, 4 portability tiers. 13 NEEDS-EDIT + 7 NEEDS-MAJOR-WORK identified for EXPANDED Path Y. Kiro CLI global pattern investigated (ADR at `docs/plans/kiro-cli-global-install-pattern-investigation-2026-05-12.md`).

## Where I Stopped

Allen is exiting + re-entering the ivco/ session so the new `~/.claude/skills/agent-talk-3round/` global install takes effect (Claude Code skill loader re-scans on new session).

Next entry point: verify `/agent-talk` activates from ivco/ cwd (no longer needs per-project copy). Then proceed to Path Y W3 (Codex adversarial review of SKILL.md v1.7.3).

## Must-Do (next session, ordered)

1. **Verify global agent-talk skill active** — at session start, confirm `/agent-talk` or `agent-talk` activates and loads SKILL.md v1.7.3 from `~/.claude/skills/agent-talk-3round/`. Quick: check skill header says v1.7.3.

2. **Path Y W3 — Codex adversarial review (D10.2 gate, non-negotiable):**
   - Write per-wave checklist `docs/plans/agent-talk-3round-global-install-2026-05-12-W3-checklist.md` first (D13)
   - Dispatch Codex to review: SKILL.md v1.7.3 + Hermes mirror v1.3.0 + `.agents/` disposition
   - If ≥5 findings → verifier-parallel rule (one fixer Ge + one auditor Ge, both dispatched same message)
   - D10.2: adversarial FIRST, internal B-Test SECOND. Never reversed.

3. **Path Y W4 — commit+push + observation row:**
   - After W3 clears: atomic commit of SKILL.md v1.7.3 + Hermes cmux-wake-plane v1.3.0 to allen-ai-os
   - Append observation row: category `global-skill-install-agent-talk-3round`
   - Update goal file status → SHIPPED

4. **ivco renovation W3 — root MD frontmatter + mirrors (5 files):**
   - Files: `CLAUDE.md`, `AGENTS.md`, `PROGRESS.md`, `TODO.md`, `allen-framework-tsmc-owners-earning.md`
   - Action: add CEM frontmatter + create obsidian symlink mirrors
   - D16 dispatch brief required. Batch ≤10 (5 files here = safe). Ge(opus) dispatch.
   - Allen checkpoint required at every wave boundary before W4 starts.

5. **ivco renovation W4-W10** — subsequent waves per W2 plan. Each needs Allen checkpoint before proceeding.

6. **EXPANDED Path Y — all 13 NEEDS-EDIT Show skills** — make session-lifecycle skills (sc, ss, save, brain, si, etc.) globally available. Requires separate D13 goal+checklist (not yet written). DO NOT start without D13 pair.

7. **D5 systemic structural fix (carry)** — pre-commit hook scanning staged diff for credential patterns across all fisher/ repos. Root cause of P0 incident. Pattern file needed.

## Must-NOT-Do

- **Do NOT commit SKILL.md v1.7.3 or Hermes mirror before W3 Codex adversarial review passes.** D10.2 violation if reversed.
- **Do NOT start EXPANDED Path Y without a D13 goal+checklist pair.** D13 gate — D17 prior plan (Path Y W4 must ship first).
- **Do NOT touch `.specify/` or `.codex/` or `.hermes.md` in ivco** — cross-agent files, out of scope per ownership boundary.
- **Do NOT commit or push any ivco renovation wave without Allen checkpoint at wave boundary.** D17 gate.
- **Do NOT rewrite ivco file content** — frontmatter + mirror + governance pointers only. Content renovations are out of scope.
- **Do NOT run new planning work** without checking D17 prior plans list above.

## Traceability

### Path Y files (staged, not committed)
- `projects/allen-ai-os/.claude/skills/agent-talk-3round/SKILL.md` — v1.7.3 (on disk, not committed)
- `projects/allen-ai-os/docs/hermes/skills/agent-talk-3round/references/cmux-wake-plane-20260430.md` — v1.3.0 (on disk, not committed)
- `~/.claude/skills/agent-talk-3round/` — 4 symlinks to canonical (filesystem only, not in git)

### Path Y committed (allen-ai-os)
- Goal: `docs/plans/agent-talk-3round-global-install-2026-05-12-goal.md`
- Checklist: `docs/plans/agent-talk-3round-global-install-2026-05-12-checklist.md`
- ADR: `docs/plans/agent-talk-3round-global-install-W1-adr-2026-05-12.md`
- W2 checklist: `docs/plans/agent-talk-3round-global-install-2026-05-12-W2-checklist.md`
- Kiro pattern: `docs/plans/kiro-cli-global-install-pattern-investigation-2026-05-12.md`
- Skill inventory: `docs/plans/show-skill-surface-inventory-2026-05-12.md`
- ivco entry-point audit: `docs/plans/ivco-entry-point-tier-docs-audit-2026-05-12.md`

### ivco renovation committed (allen-ai-os)
- Goal: `docs/plans/ivco-doc-architecture-renovation-2026-05-12-goal.md`
- Checklist: `docs/plans/ivco-doc-architecture-renovation-2026-05-12-checklist.md`
- W1 audit: `docs/plans/ivco-doc-architecture-renovation-2026-05-12-W1-audit-report.md`
- W2 plan: `docs/plans/ivco-doc-architecture-renovation-2026-05-12-W2-plan.md`

### P0 Security
- Redaction: ivco commit `31ff654` (TODO.md line 101)
- Credential: `~/.config/env/supabase.env` → `SUPABASE_DB_PASSWORD_GACTTXNL` (appended, not replaced)
- Observation: `memory/observations/index.jsonl` 2026-05-12T13:16:00Z category `credential-in-public-git-history`

## Active Plans & Checklists

| Path | Type | Status | Next action |
|------|------|--------|-------------|
| `projects/allen-ai-os/docs/plans/agent-talk-3round-global-install-2026-05-12-goal.md` | D13 goal | ACTIVE — W2 done, W3 pending | Write W3 checklist → Codex adversarial review |
| `projects/allen-ai-os/docs/plans/agent-talk-3round-global-install-2026-05-12-checklist.md` | D13 checklist | ACTIVE — W2 checked, W3-W4 unchecked | W3 Codex review gate |
| `projects/allen-ai-os/docs/plans/ivco-doc-architecture-renovation-2026-05-12-goal.md` | D13 goal | ACTIVE — W2 done, W3 pending | Allen W2→W3 checkpoint → W3 dispatch |
| `projects/allen-ai-os/docs/plans/ivco-doc-architecture-renovation-2026-05-12-checklist.md` | D13 checklist | ACTIVE — W1+W2 checked, W3-W10 unchecked | Allen checkpoint → W3 Ge(opus) dispatch |
| `projects/allen-ai-os/docs/plans/show-skill-surface-inventory-2026-05-12.md` | inventory | COMPLETE — reference only | Feed into EXPANDED Path Y D13 goal (not yet written) |

## System Health (at checkpoint)

- **Git state**: ivco clean (31ff654 pushed). allen-ai-os has staged SKILL.md + Hermes changes (uncommitted intentionally — awaiting W3).
- **Supabase MCP**: installed `--scope user`, read-only. Token in `~/.config/env/supabase.env`.
- **Global skill**: `~/.claude/skills/agent-talk-3round/` 4-file symlinks in place. Takes effect next session start.
- **P0**: CLOSED. Old credential invalidated (password rotated). Public git now has only redacted version.
- **Observations**: `memory/observations/index.jsonl` — `credential-in-public-git-history` row appended S263.
