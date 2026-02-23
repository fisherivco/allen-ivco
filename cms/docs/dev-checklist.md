# CMS Development Pre-Flight Checklist

Use this checklist before starting any Payload CMS feature/fix work.

## 1. Sync branch and scope
- [ ] Confirm target branch and task scope.
- [ ] Run `git status --short` and verify unrelated local changes are understood.

## 2. Verify environment variables
- [ ] Ensure required env vars are present in `.env` (at minimum `PAYLOAD_SECRET` and `DATABASE_URI`/`DATABASE_URL` used by this project).
- [ ] If env keys changed, update `.env.example`.

## 3. Identify security impact first
- [ ] List affected collections/globals and decide access rules (read/create/update/delete).
- [ ] If using Local API with a `user`, explicitly set `overrideAccess: false`.

## 4. Plan schema and type impact
- [ ] Identify schema changes (fields, hooks, access, globals, blocks).
- [ ] Note downstream type consumers (`payload-types.ts`, API routes, components).

## 5. Validate hook safety
- [ ] For nested operations inside hooks, always pass `req`.
- [ ] Add loop guards (`context` flags) if hooks can trigger updates/deletes recursively.

## 6. Implement minimal, atomic change
- [ ] Keep edits focused to the feature.
- [ ] Avoid broad refactors in the same commit.

## 7. Regenerate generated artifacts
- [ ] Run `npm run generate:types` after schema changes.
- [ ] Regenerate import map if components/admin imports changed.

## 8. Run static/type validation
- [ ] Run `npx tsc --noEmit` and fix all type errors.
- [ ] Run lint/tests relevant to changed modules.

## 9. Verify behavior locally
- [ ] Test happy path + permission boundaries (admin/editor/user/anonymous where applicable).
- [ ] Test create/update/delete and confirm hooks/transactions behave correctly.

## 10. Final review before commit
- [ ] Re-run `git diff --name-only` to confirm only intended files changed.
- [ ] Write a Conventional Commit message (`fix:`, `feat:`, `refactor:`, etc.).
