---
title: IVCO Codex Session Governance
status: ACTIVE
version: 2026-05-12.1
date: 2026-05-12
owner: macmini codex-cli Chi
canonical_path: projects/ivco/docs/governance/codex-session-governance.md
mirror: obsidian/projects/ivco/governance/codex-session-governance.md
project: ivco
---

# IVCO Codex Session Governance

This is the Codex-owned governance entrypoint for working from
`projects/ivco/`. Keep it small: session mechanics live in global Codex skills,
project facts live in IVCO project docs, and evidence lives in task or handoff
records.

## Load Order

1. `projects/ivco/AGENTS.md` — Codex runtime router for this repo.
2. This file — IVCO-specific Codex session and document-governance rules.
3. `projects/allen-ai-os/docs/ivco-context-index.md` — cross-project IVCO
   context index and current project status.
4. Task-specific project docs:
   - `projects/ivco/docs/ivco-dna.md`
   - `projects/ivco/allen-framework-tsmc-owners-earning.md`
   - `projects/ivco/docs/expert-manual-v2.md`
   - `projects/ivco/cms/AGENTS.md` for Payload CMS work

## Session Commands

Codex session commands are global skills and are available from `projects/ivco/`
without project-local copies:

| Command | Skill | Behavior from IVCO |
|---|---|---|
| `$sc` | `sc` | Resumes the global Codex lane from `projects/allen-ai-os/docs/plans/codex/INDEX.md`. |
| `$ss` | `ss` | Writes the active Codex checkpoint handoff in the global Codex lane. |
| `$save` | `save` | Writes the final Codex handoff, closes the global Codex lane, and performs scoped save closure. |
| agent talk | `agent-talk-3round` | Uses shared JSONL transport plus cmux notice-only wake when a peer runtime must receive a bounded request. |

Do not fork `$sc`, `$ss`, or `$save` into IVCO-local commands. The command path
is global skill -> shared session engine -> canonical handoff. IVCO-specific
work is referenced from the global handoff via plans, checklists, task files,
and this governance entrypoint.

## Handoff Model

Default live Codex handoff authority remains:

| Surface | Canonical | Mirror |
|---|---|---|
| Codex lane index | `projects/allen-ai-os/docs/plans/codex/INDEX.md` | `obsidian/projects/allen-ai-os/handoffs/codex/INDEX.md` |
| Codex lane handoffs | `projects/allen-ai-os/docs/plans/codex/` | `obsidian/projects/allen-ai-os/handoffs/codex/` |

IVCO also has a reserved Codex project handoff namespace for explicitly
project-local handoffs:

| Surface | Canonical | Mirror |
|---|---|---|
| IVCO Codex project handoffs | `projects/ivco/docs/plans/codex/` | `obsidian/projects/ivco/handoffs/codex/` |

Use the IVCO project namespace only when Allen explicitly asks for a project
handoff separate from the global Codex lane. Otherwise, record IVCO work in the
global Codex handoff and cite the IVCO project artifacts.

## Document Governance

Markdown uses canonical local write plus same-transaction Obsidian symlink
mirror. Non-Markdown stays local-first and git-managed.

Codex-owned IVCO mappings:

| Artifact | Canonical | Mirror |
|---|---|---|
| Root runtime routers | `projects/ivco/` | `obsidian/projects/ivco/root/` |
| Governance | `projects/ivco/docs/governance/` | `obsidian/projects/ivco/governance/` |
| Project tasks | `projects/ivco/tasks/` | `obsidian/projects/ivco/tasks/` |
| Codex project handoffs | `projects/ivco/docs/plans/codex/` | `obsidian/projects/ivco/handoffs/codex/` |

Before adding new IVCO Markdown, read:

- `projects/allen-ai-os/docs/governance/document-governance-index.md`
- `projects/allen-ai-os/docs/governance/document-write-policy.md`
- `projects/allen-ai-os/docs/governance/context-entropy-management-governance.md`

Then run `tools/canonical-search-before-create.sh <basename>`, write the
canonical file, create the mirror symlink in the same transaction, and run the
mirror checker.

## Runtime Ownership

Codex owns or may update:

- `projects/ivco/AGENTS.md`
- `projects/ivco/docs/governance/codex-session-governance.md`
- `projects/ivco/tasks/**` when the task is Codex-owned
- `projects/ivco/docs/plans/codex/**` when a project-local Codex handoff is
  explicitly requested

Codex does not own:

- `projects/ivco/CLAUDE.md`
- `projects/ivco/.claude/**`
- `projects/ivco/.hermes.md`
- `projects/ivco/docs/plans/kiro/**`

Send peer-runtime suggestions through `agent-talk-3round`; do not edit peer
private runtime files from Codex.

## Legacy Obsidian Copies

Regular files under `obsidian/projects/ivco/*.md` and
`obsidian/projects/ivco/blog/*.md` are pre-local-first content copies, not a
standing write surface. Do not edit them directly. Handle them only through a
dedicated triage/rematerialization plan that preserves content and replaces the
read path with symlinks.

## Field Reports

- `docs/governance/ivco-kiro-agent-talk-field-report-20260512.md` records the
  first successful IVCO-directory `agent-talk-3round` handshake between
  `macmini codex-cli Chi` and `kiro-cli`, including cmux surface selection,
  JSONL payload discipline, and reusable Kiro participation rules.

## Verification

Use these checks before claiming IVCO Codex governance work is complete:

```bash
python3 /Users/fisherivco/fisher/tools/lib/canonical_mirror_map.py --smoke
/Users/fisherivco/fisher/tools/canonical-collision-check.sh --obsidian-mirror
python3 -c 'import pathlib,tomllib; tomllib.loads(pathlib.Path("/Users/fisherivco/.codex/config.toml").read_text()); print("TOML_OK")'
```

## Changelog

| Version | Date | Change |
|---|---|---|
| 2026-05-12.1 | 2026-05-12 | Initial Codex-owned IVCO session governance entrypoint. |
