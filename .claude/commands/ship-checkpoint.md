---
description: Refresh state.md, stage tracked docs + source, draft commit message, output /compact hint. Does NOT commit.
---

Run the ship-checkpoint protocol from [`docs/workflow-notes.md`](../../docs/workflow-notes.md#ship-checkpoint--claude-initiated-state--commit-prep--compact). End-to-end:

## 1. Refresh `docs/state.md`

Update it to reflect *right now* — what just landed, recent decisions, open questions, next steps, gotchas. Same rules as `/state`:

- Don't pad empty sections.
- Replace stale entries; preserve still-relevant ones.
- End with `_Last updated: <YYYY-MM-DD> — <one-line context>_`.
- Touches only `docs/state.md`.

## 2. Stage files explicitly

Stage in this order, by explicit `git add <path>` (NEVER `-A` / `.`):

- All source files touched this session
- All `docs/*.md` touched this session **except**:
  - `docs/handoff.md`
  - `docs/my-log.md`
- `schema.sql`, `pyproject.toml`, or any other tracked file touched

Then run `git status` so the user sees exactly what's staged and what isn't. Confirm `handoff.md` / `my-log.md` are still untracked or unstaged.

## 3. Draft the commit message (do NOT commit)

Check recent commit-message style with `git log --oneline -10`. Match the same prefix convention and length. Offer two options:

- **Verbose** — 5–8 bullets summarising the changes
- **One-liner** — a single descriptive line

Present both. Do **not** run `git commit`.

## 4. Hand off to user with the `/compact` hint

End the response with these four numbered next steps for the user:

1. `git diff --cached` (optional review)
2. `git commit -m "..."` (pick one of the drafted messages)
3. `git push origin main`
4. `/compact preserve <specific load-bearing context for this session>`

The `/compact` hint must be tailored to what *this* session was building — list locked decisions, scope, what's implemented, what's next, and any tone/protocol invariants worth preserving. Pre-write it ready to paste.

## Constraints

- **Do NOT commit.** User reviews the staged diff first.
- **Do NOT push.** User pushes manually.
- **Do NOT run `/compact` yourself.** It's a built-in command the user invokes. Just hand them the hint.
- Never use `git add -A` or `git add .` — stage by explicit path.
- Never stage `docs/handoff.md` or `docs/my-log.md`.
- Skip this protocol mid-flight in a coherent task — wait for the natural seam.
