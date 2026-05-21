# Project state — AIFeeder (Mindful Content Feed)

## Current focus

**UI iteration round 1 complete + source-edit modal landed (first UI-→-DB write path) — paused for next browser-check before wiring `refresh`.** All 14+ feedback items from the first browser-check executed (sidebar polish, home cards, content page, avatar restructure across 2 iterations, 3 iterations on the card-title highlight). Source-edit modal is the newest surface — clicking a sidebar source opens a centered modal that blurs the main column (sidebar stays sharp via z-index), URL + why edits persist to the real `sources` table via a new `web/writes.py` module. Next is browser-check round 2 → `/refresh` wiring → real-world test.

Working title: *Mindful Content Feed* — intent-filtered, mindful consumption. v1 audience: the builder.

## Recent decisions

Full A-category reasoning in [`docs/decisions.md`](decisions.md); B-category in [`docs/engineering-decisions.md`](engineering-decisions.md). UX/UI deliberation in [`docs/conversation/2026-05-20_b670_ux-design.md`](conversation/2026-05-20_b670_ux-design.md). Most relevant since last refresh:

- **Sources are user-editable from the UI** — first UI-→-DB write path in v1. Click a sidebar source → centered modal (backdrop blurs main column, sidebar z-indexed above), URL + why fields, save persists via new [`web/writes.py`](../src/aifeeder/web/writes.py) using `UPDATE sources SET url = ?, why = ?`. Knock-on: the modal pattern becomes the in-house convention; `repo.py` stays read-only by design; `web/writes.py` is the natural home for future archive/delete/mark-read UI writes.
- **First browser-check feedback round (5 A-decisions + 9 B-decisions)** — thumbs supersedes the locked "icon arrows not thumbs"; plain-block content callout supersedes the sticky-note; Source Sans 3 body typography refines the 2026-05-20 typography lock; apple yes/maybe indicators on home cards (whole = yes, 3/4-eaten = maybe); in-text highlighting + quote-attached notes (B→A escalation — touches scope, schema-shape, and the note-taking interaction model).
- **Avatar restructure** — the shaded radial-gradient circle is now the *head* (not a background); a matching shaded dome below it is the *body*; dark-brown silhouette layer removed entirely. Supersedes the round-1 "silhouette-inside-the-circle" engineering fix.
- **Collapsed-sidebar polish** — when collapsed, only the orange `+` stays visible at the top; gear / profile-icon / top-chevron all `display: none`. The expand-handle tab moves from vertical-centre to `top: 0.9rem` so it visually takes over the chevron's role.
- **Card title highlight (3 iterations today)** — final shape: per-line bands with transparent top/bottom margins via `linear-gradient(transparent 12%, accent 12%, accent 88%, transparent 88%)` + `box-decoration-break: clone`. Iterations were (a) raise gradient stop 60%→40% (still bottom-anchored band), (b) full-coverage paint (made adjacent lines visually merge), (c) per-line bands with transparent margins (current).

### v1 slice scope (unchanged)

- **Sources:** Simon Willison (RSS) + ArXiv `cs.AI` (RSS). YouTube/Struthless still deferred to next session.
- **In:** RSS ingest, AI summarize, list view, detail view, manual refresh, "open original" link, faked notes + favourites UI, **source edit (URL + why) — now real DB write**.
- **Out (schema ready, UI deferred or stubbed):** real thumbs feedback persistence, library archive UI, source mgmt UI for add/delete (only edit landed today), sortable list, cost dashboard, chapter index, periodic "why" revisit.

### Failure recovery (locked, not yet wired)

Transient → 3 retries with exponential backoff (1s/4s/16s); permanent → no retry; content-level → skip; unknown → 1 retry then permanent. Sources with `consecutive_failures >= 3` get a `!` icon. Schema columns exist; logic lands with `refresh`.

## What's implemented

- `aifeeder init` — apply schema, seed sources + user row
- `aifeeder preview` — fetch + summarize + stdout, no DB writes (validated end-to-end)
- `aifeeder seed-fake` — 12 fixture items spanning all 9 content_type_tags for UI dev (idempotent)
- `aifeeder serve` — local FastAPI + HTMX + Jinja2 UI on 127.0.0.1:8000
- **Web UI** —
    - Loading → home → content + Library/Favourites/Notes placeholder pages
    - **Sidebar:** Home button + Library/Favourites/Notes + alphabetical source list (now HTMX-triggers source-edit modal); shaded-head + shaded-body avatar with thought-bubbles on hover; expand-handle tab visible when collapsed
    - **Home cards:** apple verdict indicators (whole=yes, 3/4-eaten=maybe), Source Sans 3 body font, per-line title highlights with transparent top/bottom margins
    - **Content page:** plain-block "why" callout (purpose + key_points), thumbs up/down feedback, in-text selection → floating "+ Note" → quote-attached note + persistent `<mark>` highlight on reload
    - **Source-edit modal** — click a sidebar source → centered modal blurs main column (sidebar stays sharp via `z-index: 250` above backdrop `z-index: 200`); URL + why fields with helper hint; close on Esc / backdrop-click / Cancel; duplicate-URL collisions gracefully re-render the modal with a `.modal-error` callout (not 500)
- **HTMX endpoints:** feedback callout, note panel (with quote pre-fill), favourite toggle, source modal edit + save
- 7 page routes + 7 HTMX endpoints return 200 in smoke test; happy-path and error-path source-edit verified

## Open questions

1. **Source of "user-level whys" (deferred).** v1 loading page uses per-source whys directly. AI-derived user-level intent statements remain a future surface, not blocking.
2. **Ritual fit.** Replace doomscrolling without becoming another "must check" app. Load-bearing through build.
3. **Home page intentionality.** "Anything AI recommended" is the v1 default; the question of *what should the home page intentionally show* (unread-only? today's-only? hand-curated?) is provisional — see [decisions.md → 2026-05-21 — Home cards stay unchanged](decisions.md). Affects the read-state dimming idea ([ideas.md → UI/UX](ideas.md)).
4. **iframe vs. recommendation-surface leak.** Not relevant in v1 (no YouTube). Tracked for v2.
5. **Add-source affordance.** The orange `+` button in the sidebar is wired but currently a no-op — open question whether to reuse the source-edit modal pattern for *creating* sources or wait until the schema-driven discovery flow lands. Noted as a follow-on in [decisions.md → 2026-05-21 — Sources are user-editable from the UI](decisions.md).

## Next steps

In order:

1. **User browser-check round 2** — open `localhost:8000`, retest the UI iteration items (sidebar collapse animation feel, apple sizing, sans/serif balance, expand-handle position when collapsed, per-line title highlights, content-page plain block, thumbs, selection → note flow, source-edit modal). Flag remaining issues.
2. **UI fix iteration round 2** based on user feedback (likely 1 round, smaller scope).
3. **Wire `refresh` subcommand** — ingest + summarize + persist to DB; includes failure-recovery retry policy + `consecutive_failures` / `last_error_*` population on sources. This is where the in-memory fakes (notes / favourites / highlights) become real schema.
4. **Real-world test** + fix top 1–2 issues.
5. **Next session:** YouTube/Struthless (`yt-dlp` + transcript pipeline); real notes/favourites/highlights schema migration.

## Gotchas / quirks

- **UI iteration round 1 verified server-side, not visually verified.** Smoke test = all routes 200 + HTML structure + persistence + error paths correct. Browser visual pass (animation timing, apple sizing, sans/serif balance, modal backdrop blur, selection-popup placement) still owed by user.
- **Modal pattern is the in-house convention.** `partials/source_modal.html` + `.modal-backdrop` + `.modal-card` + Esc/click-outside/cancel close + `HX-Refresh: true` on save. Future modals reuse this shape rather than inventing a new one.
- **`web/writes.py` is the first real UI-→-DB write path.** `repo.py` stays read-only by design; `fakes.py` stays for in-memory fakes (notes/favourites/highlights). New UI writes that need real persistence go in `writes.py`.
- **`sources.url` carries a `UNIQUE` constraint.** Editing a source's URL to one already used by another source raises `sqlite3.IntegrityError`; the route catches this and re-renders the modal with a `.modal-error` callout (no 500). Worth remembering when wiring `refresh` (which also inserts sources via `INSERT OR IGNORE`).
- **Notes + favourites + highlights are UI-faked in v1** — in-memory dicts in [`src/aifeeder/web/fakes.py`](../src/aifeeder/web/fakes.py); wiped on server reload. Real schema lands with `refresh` wiring. Highlights use naïve substring-match (first occurrence per paragraph) — corner case if the same phrase appears twice.
- **Quote-attached note save uses `HX-Refresh: true`** so the page reloads with the new `<mark>` rendered server-side. Same pattern reused by the source-edit save.
- **Two Starlette gotchas baked into routes.py** — `TemplateResponse(request, name, ctx)` signature (request first); FastAPI route order matters (`/feedback/{id}/refine` registered BEFORE `/feedback/{id}/{direction}` to prevent the generic catching "refine").
- **`users` table addition partially supersedes the 2026-05-20 local-only "no forward-compat scaffolding" line** — the `users` parent table is in v1; `items.user_id` etc. are still deferred. See [`decisions.md`](decisions.md) → 2026-05-21 — `users` table.
- **`docs/handoff.md` and `docs/my-log.md` intentionally untracked** — never `git add .` or `-A`; always stage explicitly. The `/ship-checkpoint` skill stages by path.
- **Three parallel Claude Code sessions ran on this checkout earlier** (b670 = strategy + scaffold + AI + UX + UI + iteration; 10ca = hook debugging; 4dac = git/auth setup). `state.md` is single-writer — serialise `/state` between concurrent sessions or use `git worktree`.
- **Schema includes future-MVP columns the slice doesn't use yet** (`failure_class`, `failure_message`, `consecutive_failures`, `last_error_at`, `last_error_message`, `is_read`, `feedback` table, `chapter_index_json`).
- **`init` + `seed-fake` are idempotent** — `init` applies schema + seeds sources + user; `seed-fake` inserts 12 items only if missing. Re-runs are no-ops. **Caveat:** if a source's URL has been UI-edited between init runs, the original seeded URL becomes "available" again and a re-`init` will create a duplicate source row (discovered + cleaned up during today's smoke test). When `refresh` lands, document the right workflow for re-syncing.
- **DB file is local-only.** If `aifeeder.db` exists from before the `users`-table addition, `serve` will work but `get_user()` returns the fallback `{"id": 1, "name": "you"}` instead of `Emma` — delete the file and re-`init` to fix.
- **"Open original" link bypasses in-app reader in v1 slice.** Fine for Simon + ArXiv. Mission-compromise flag lights up when YouTube enters v2.
- **Never instrument engagement metrics** (DAU, session length). Mission-aligned metrics only.
- **The mindfulness paradox** — every UX decision: if it would feel at home in TikTok, it doesn't belong here.
- **AI prompt tone is A-category.** Locked phrasings ("Worth reading if…" / "Worth a shot for X although Y" / "Skip — this is mostly Z") — never change without user sign-off.
- **Conversation log format:** per-turn entries are brief **Me:** / **Claude:** intent-summary — never a verbatim repaste of the chat reply, even when in-character. Memory rule: [feedback_conversation-log-no-transcripting](/home/emma/.claude/projects/-home-emma-Workspace-Make-Land-AIFeeder/memory/feedback_conversation-log-no-transcripting.md).
- **Completeness rule for decisions** — every concrete decision reached must land in decisions.md (A) or engineering-decisions.md (B) the same turn, not only the conversation log. See [CLAUDE.md → Completeness rule](../CLAUDE.md#completeness-rule--no-concrete-decision-lives-only-in-conversation). Heavily exercised today (6 A-entries + 16 B-entries logged across 5 user turns).
- **IDE flags `schema.sql` errors** — false positives from the MSSQL language server; file is valid SQLite.

_Last updated: 2026-05-22 — UI iteration round 1 + source-edit modal (first UI-→-DB write path) complete; paused for browser-check round 2 before wiring `refresh`._
