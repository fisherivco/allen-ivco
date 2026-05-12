---
title: KIRO — ivco Project Governance Entry Point
status: ACTIVE
version: 2026-05-12.1
owner: macmini kiro-cli Kiro
canonical_path: projects/ivco/docs/plans/kiro/KIRO.md
mirror: obsidian/projects/ivco/handoffs/kiro/KIRO.md
project: ivco
created: 2026-05-12
session: S262
---

# KIRO — ivco Project Governance Entry Point

Kiro CLI governance entry point for the `ivco` project. Read this file at
session start when working in `projects/ivco/`.

## Project Identity

| Item | Value |
|---|---|
| Project | IVCO — Intelligent Valuation Confidence Observatory |
| Working dir | `/Users/fisherivco/fisher/projects/ivco/` |
| Kiro lane | `ivco` |
| Handoff canonical | `projects/ivco/docs/plans/kiro/handoffs/` |
| Handoff mirror | `obsidian/projects/ivco/handoffs/kiro/` |
| Handoff index | `projects/ivco/docs/plans/kiro/handoffs/INDEX.md` |

## Session Skills

All Kiro global skills (`~/.kiro/skills/`) are available in any working
directory. No project-local skill copies needed.

| Skill | Trigger | Behavior in ivco |
|---|---|---|
| `sc` | session start | reads `projects/ivco/docs/plans/kiro/handoffs/INDEX.md` |
| `ss` | checkpoint | writes to `projects/ivco/docs/plans/kiro/handoffs/` |
| `ksave` | final save | writes to `projects/ivco/docs/plans/kiro/handoffs/` |
| `agent-talk-3round` | cross-agent | same as allen-ai-os (shared transport) |
| `research` | `/research <topic>` | same as allen-ai-os |

Lane routing is automatic: `sc`/`ss`/`ksave` detect `$PWD` contains `ivco`
and route to the ivco lane. See `~/.kiro/skills/session-engine/ENGINE.md`
§Project-Lane Routing.

## Governance References

| Document | Path | Purpose |
|---|---|---|
| Session engine | `~/.kiro/skills/session-engine/ENGINE.md` | Canonical paths, gates, lane routing |
| Handoff schema | `projects/allen-ai-os/docs/plans/kiro/kiro-handoff-schema.md` | Shared schema (allen-ai-os owned) |
| Doc write policy | `projects/allen-ai-os/docs/governance/document-write-policy.md` | Markdown write governance |
| Allen governance | `~/.kiro/steering/allen-governance-principles.md` | Cross-project principles |
| Skill creation SOP | `~/.kiro/steering/skill-creation-sop.md` | Skill lifecycle |
| ivco project DNA | `projects/ivco/docs/ivco-dna.md` | Project soul document |
| ivco AGENTS.md | `projects/ivco/AGENTS.md` | Multi-agent team contract (Codex/Claude) |

## Runtime Boundary

Kiro owns in ivco:
- `projects/ivco/docs/plans/kiro/` — handoffs, this governance file
- `obsidian/projects/ivco/handoffs/kiro/` — obsidian mirrors (symlinks only)

Kiro does NOT own:
- `projects/ivco/AGENTS.md` — Codex/Claude owned
- `projects/ivco/CLAUDE.md` — Claude Code owned
- `projects/ivco/.claude/` — Claude Code owned
- Any ivco source code, CMS, or CLI files

Cross-runtime suggestions travel through `agent-talk-3round` only.

## Handoff Frontmatter for ivco

Same schema as allen-ai-os (`KIRO-HANDOFF-SCHEMA-1.0.0`) with these values:

```yaml
canonical_path: projects/ivco/docs/plans/kiro/handoffs/<filename>
mirror: obsidian/projects/ivco/handoffs/kiro/<filename>
lane: kiro
```

## Changelog

| Version | Date | Change |
|---|---|---|
| 2026-05-12.1 | 2026-05-12 | Initial ivco KIRO.md. Session S262. |
