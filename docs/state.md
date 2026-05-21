# Project state — AIFeeder (Mindful Content Feed)

## Current focus

**UI build complete (server-side verified) — paused for user browser-check before wiring `refresh`.** All 4 pages implemented per the 18 locked design decisions (loading + home + content + sidebar partial); 12 routes return 200 in smoke test; HTML rendering verified. Browser visual pass still owed by user. Next is browser-iteration → `/refresh` wiring → real-world test.

Working title: *Mindful Content Feed* — intent-filtered, mindful consumption. v1 audience: the builder.

## Recent decisions

Full A-category reasoning in [`docs/decisions.md`](decisions.md); B-category in [`docs/engineering-decisions.md`](engineering-decisions.md). UX/UI deliberation in [`docs/conversation/2026-05-20_b670_ux-design.md`](conversation/2026-05-20_b670_ux-design.md). Most relevant since last refresh:

- **18 UX design decisions locked** + 4 new A-entries this turn — `users` table in schema (B→A escalation, partial-supersession of the 2026-05-20 no-forward-compat line); home cards stay unchanged after feedback (no hide / reflow / dim); sidebar default state asymmetric (home open / content collapsed); colour-only cards v1 (thumbnails deferred to ideas.md).
- **6 B-decisions clustered under the 2026-05-21 /plan-feature open-Q resolution** — stack pick formally adopted, `seed-fake` CLI subcommand, monogram source-logo placeholders, HTMX over vanilla `fetch`, CSS Grid `auto-flow: dense` over Masonry.js, vanilla JS for non-HTMX interactions.
- **New completeness rule in [CLAUDE.md](../CLAUDE.md#completeness-rule--no-concrete-decision-lives-only-in-conversation)** — every concrete decision reached in a turn must land in decisions.md OR engineering-decisions.md, not only in the conversation log. Backfilled 4 A-entries + 7 B-entries to demonstrate the rule.
- **New skill [`/audit-rules`](../.claude/commands/audit-rules.md)** — walks rule files + recent conversation slices, surfaces 4 classes of drift (rules-not-firing, rules-firing-noisily, rules-without-tooling, artifacts-without-rules); surfaces only, doesn't fix.
- **New section in [workflow-notes.md → How to consume a /plan-feature output (5-step loop)](workflow-notes.md#how-to-consume-a-plan-feature-output-the-5-step-loop)** — reusable pattern: read top-to-bottom → A/B rescan → push back on tradeoffs → lock in writing (decisions files, not chat) → surface escalations.

### v1 slice scope (unchanged)

- **Sources:** Simon Willison (RSS) + ArXiv `cs.AI` (RSS). YouTube/Struthless still deferred to next session.
- **In:** RSS ingest, AI summarize, list view, detail view, manual refresh, "open original" link, faked notes + favourites UI.
- **Out (schema ready, UI deferred or stubbed):** real thumbs feedback persistence, library archive UI, source mgmt UI, sortable list, cost dashboard, chapter index, periodic "why" revisit.

### Failure recovery (locked, not yet wired)

Transient → 3 retries with exponential backoff (1s/4s/16s); permanent → no retry; content-level → skip; unknown → 1 retry then permanent. Sources with `consecutive_failures >= 3` get a `!` icon. Schema columns exist; logic lands with `refresh`.

## What's implemented

- `aifeeder init` — apply schema, seed sources + user row
- `aifeeder preview` — fetch + summarize + stdout, no DB writes (validated end-to-end)
- `aifeeder seed-fake` — 12 fixture items spanning all 9 content_type_tags for UI dev (idempotent)
- `aifeeder serve` — local FastAPI + HTMX + Jinja2 UI on 127.0.0.1:8000
- **Web UI** — loading + home + content + sidebar partial + Library/Favourites/Notes placeholder pages; HTMX endpoints for feedback callout / note panel / favourite toggle; in-memory faked notes + favourites stores
- 7 routes return 200, 5 HTMX endpoints return 200, static CSS + JS served correctly

## Open questions

1. **Source of "user-level whys" (deferred).** v1 loading page uses per-source whys directly. AI-derived user-level intent statements remain a future surface, not blocking.
2. **Ritual fit.** Replace doomscrolling without becoming another "must check" app. Load-bearing through build.
3. **Home page intentionality.** "Anything AI recommended" is the v1 default; the question of *what should the home page intentionally show* (unread-only? today's-only? hand-curated?) is provisional — see [decisions.md → 2026-05-21 — Home cards stay unchanged](decisions.md). Affects the read-state dimming idea ([ideas.md → UI/UX](ideas.md)).
4. **iframe vs. recommendation-surface leak.** Not relevant in v1 (no YouTube). Tracked for v2.

## Next steps

In order:

1. **User browser-check the UI** — open `localhost:8000`, click through loading → home → content; test HTMX (feedback callout, note panel, favourite); test sidebar collapse + persona-avatar hover; flag any CSS / animation / copy issues.
2. **UI fix iteration** based on user feedback (likely 1–2 rounds).
3. **Wire `refresh` subcommand** — ingest + summarize + persist to DB; includes failure-recovery retry policy + `consecutive_failures` / `last_error_*` population on sources.
4. **Real-world test** + fix top 1–2 issues.
5. **Next session:** YouTube/Struthless (`yt-dlp` + transcript pipeline); real notes/favourites schema.

## Gotchas / quirks

- **UI is server-side verified, not visually verified.** Smoke test = all routes 200 + HTML structure correct. Browser visual pass (masonry gaps, mix-blend-mode circle blending, sticky-note rotation, animation easing) still owed by user.
- **Notes + favourites are UI-faked in v1** — in-memory dicts in [`src/aifeeder/web/fakes.py`](../src/aifeeder/web/fakes.py); wiped on server reload. Real schema lands with `refresh` wiring.
- **Two Starlette gotchas fixed during smoke test** — (a) `TemplateResponse(name, ctx)` now wants `(request, name, ctx)` — old signature silently passes name as request, dict as name, crashes deep in jinja cache lookup; (b) FastAPI route order matters — `/feedback/{id}/refine` had to land *above* `/feedback/{id}/{direction}` or "refine" gets caught as a direction value.
- **`users` table addition partially supersedes the 2026-05-20 local-only "no forward-compat scaffolding" line** — the `users` parent table is in v1; `items.user_id` etc. are still deferred. See [`decisions.md`](decisions.md) → 2026-05-21 — `users` table.
- **`docs/handoff.md` and `docs/my-log.md` intentionally untracked** — never `git add .` or `-A`; always stage explicitly. The `/ship-checkpoint` skill stages by path.
- **Three parallel Claude Code sessions ran on this checkout earlier** (b670 = strategy + scaffold + AI + UX + UI; 10ca = hook debugging; 4dac = git/auth setup). `state.md` is single-writer — serialise `/state` between concurrent sessions or use `git worktree`.
- **Schema includes future-MVP columns the slice doesn't use yet** (`failure_class`, `failure_message`, `consecutive_failures`, `last_error_at`, `last_error_message`, `is_read`, `feedback` table, `chapter_index_json`).
- **`init` + `seed-fake` are idempotent** — `init` applies schema + seeds sources + user; `seed-fake` inserts 12 items only if missing. Re-runs are no-ops.
- **DB file is local-only.** If `aifeeder.db` exists from before the `users`-table addition, `serve` will work but `get_user()` returns the fallback `{"id": 1, "name": "you"}` instead of `Emma` — delete the file and re-`init` to fix.
- **"Open original" link bypasses in-app reader in v1 slice.** Fine for Simon + ArXiv. Mission-compromise flag lights up when YouTube enters v2.
- **Never instrument engagement metrics** (DAU, session length). Mission-aligned metrics only.
- **The mindfulness paradox** — every UX decision: if it would feel at home in TikTok, it doesn't belong here.
- **AI prompt tone is A-category.** Locked phrasings ("Worth reading if…" / "Worth a shot for X although Y" / "Skip — this is mostly Z") — never change without user sign-off.
- **Conversation log format:** per-turn entries are brief **Me:** / **Claude:** intent-summary — never a verbatim repaste of the chat reply, even when in-character. Memory rule: [feedback_conversation-log-no-transcripting](/home/emma/.claude/projects/-home-emma-Workspace-Make-Land-AIFeeder/memory/feedback_conversation-log-no-transcripting.md).
- **Completeness rule for decisions** — every concrete decision reached must land in decisions.md (A) or engineering-decisions.md (B) the same turn, not only the conversation log. See [CLAUDE.md → Completeness rule](../CLAUDE.md#completeness-rule--no-concrete-decision-lives-only-in-conversation).
- **IDE flags `schema.sql` errors** — false positives from the MSSQL language server; file is valid SQLite.

_Last updated: 2026-05-21 — UI build complete (server-side smoke-tested); paused for user browser-check before wiring `refresh`._
