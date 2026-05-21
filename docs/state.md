# Project state — AIFeeder (Mindful Content Feed)

## Current focus

**End of the AI-prompt half of the v1 5-hour slice.** The summarization pipeline is implemented, the v1 prompt is locked, and real outputs from Simon + ArXiv have passed the A-checkpoint. Next is the **UX brief from user**, then build the FastAPI + HTMX + Jinja2 list/detail/refresh UI, then wire `refresh` (ingest + summarize + persist), then real-world test.

Working title: *Mindful Content Feed* — intent-filtered, mindful consumption. v1 audience: the builder.

## Recent decisions

Full A-category reasoning in [`docs/decisions.md`](decisions.md); B-category engineering choices in [`docs/engineering-decisions.md`](engineering-decisions.md). Most relevant since last refresh:

- **Local-only, single-user v1.** No auth, no multi-tenancy, no hosting, no billing. Single-user-only schema; migration accepted as future cost.
- **Single general AI prompt; defer content-type-adaptive.** Adaptive prompting deferred to [ideas.md](ideas.md). Content-type classification still happens (display).
- **AI prompt design (locked, validated):** conversational tone ("Worth reading if…" / "Worth a shot for X although Y" / "Skip — this is mostly Z"), fixed format taxonomy, short-bullet key points (8–12 words), confidence score (0.0–1.0) alongside yes/no/maybe verdict, 2 few-shots in system prompt. Both `yes` and `maybe` show; only `no` is hidden.
- **Summary schema additions:** `confidence`, `purpose` (author intent, one sentence), `read_time_estimate` (quick / medium / long buckets), `style_tag` (orthogonal to `content_type_tag` — 7-value vocabulary: technical-deep-dive, explainer, opinionated, conversational, reflective, news-brief, narrative). Total classification fields now = 3 (content_type_tag, style_tag, read_time_estimate). At the edge of "too many" — UX brief decides what surfaces in list vs. detail.
- **Tech stack: Python 3.11+ + FastAPI + HTMX + Jinja2 + SQLite (stdlib).** LLM via OpenAI SDK, default `gpt-4o-mini`. Anthropic abstracted but unused.
- **A/B/C decision framework.** A = user owns, B = Claude decides + briefs inline, C = Claude just does. Pre-session checklist in [workflow-notes.md](workflow-notes.md#design-decision-spectrum-abc-split).
- **New ship-checkpoint protocol** added to [workflow-notes.md](workflow-notes.md#ship-checkpoint--claude-initiated-state--commit-prep--compact): Claude proposes state refresh + commit prep + /compact at natural pauses; user controls the commit + push.

### 5-hour slice scope (unchanged)

- **Sources:** Simon Willison (RSS) + ArXiv `cs.AI` (RSS). **Struthless YouTube still deferred** to next session (yt-dlp ~2 hrs).
- **In:** RSS ingest, AI summarize, list view, detail view, manual refresh, "open original" link.
- **Out (schema ready, UI deferred):** thumbs feedback, library archive UI, source mgmt UI, sortable list, cost dashboard, chapter index, periodic "why" revisit.

### Failure recovery (locked, not yet wired)

Transient → 3 retries with exponential backoff (1s/4s/16s); permanent → no retry; content-level → skip; unknown → 1 retry then permanent. Sources with `consecutive_failures >= 3` get a `!` icon. Schema columns exist; logic lands with `refresh`.

## Open questions

1. **UX brief from user.** Now is the moment — what does the list look like, what's the detail view, what surfaces where (verdict / confidence / reason / purpose / 2 tags / read-time / key-points), empty-state copy, refresh interaction, mindful-tone constraints. **Until this lands, no UI code is written.**
2. **Ritual fit.** Replace doomscrolling without becoming another "must check" app. Resolve before the reader UI.
3. **iframe vs. recommendation-surface leak.** Not relevant in v1 slice (no YouTube). Tracked for v2.

## Next steps

In order:

1. **PAUSE — UX brief from user.** What pages exist, what they look like, what fields surface where.
2. **Build UX** — FastAPI + HTMX + Jinja2 per user direction.
3. **Wire `refresh` subcommand** — ingest + summarize + persist to DB (currently raises `NotImplementedError`). Includes the failure-recovery retry policy.
4. **Add failure-class detection** to ingest + ai paths; populate `consecutive_failures` / `last_error_*` on sources.
5. **Real-world test** + fix top 1–2 issues.
6. **Next session:** YouTube/Struthless (`yt-dlp` + transcript pipeline).

## Gotchas / quirks

- **Three parallel Claude Code sessions ran on this checkout earlier** (b670 = strategy + scaffold + AI implementation; 10ca = hook debugging; 4dac = git/auth setup). `state.md` is single-writer — serialise `/state` between concurrent sessions or use `git worktree` for branch-divergent work.
- **Schema includes future-MVP columns the slice doesn't use yet** (`failure_class`, `failure_message`, `consecutive_failures`, `last_error_at`, `last_error_message`, `is_read`, `feedback` table, `chapter_index_json`).
- **`preview` auto-applies the schema** — was opaque sqlite errors before; now idempotent.
- **DB file is local-only.** If you ran `aifeeder init` before the latest schema additions (`purpose`, `style_tag`, `read_time_estimate`), `refresh` will fail on write. Solution: delete the file and re-`init`. No data lost — nothing persisted yet.
- **"Open original" link bypasses in-app reader in v1 slice.** Fine for Simon + ArXiv. Mission-compromise flag lights up when YouTube enters v2.
- **`docs/handoff.md` and `docs/my-log.md` intentionally untracked** — never `git add .` or `-A`; always stage explicitly.
- **Never instrument engagement metrics** (DAU, session length). Mission-aligned metrics only.
- **The mindfulness paradox** — every UX decision: if it would feel at home in TikTok, it doesn't belong here.
- **AI prompt tone is A-category.** If quality is off after more outputs, iterate the prompt — never the tone phrasings ("Worth reading if…" / "Worth a shot for X although Y" / "Skip — this is mostly Z") without user sign-off.
- **IDE flags `schema.sql` errors** — false positives from the MSSQL language server; file is valid SQLite.

_Last updated: 2026-05-21 — AI prompt validated end-to-end via `aifeeder preview`; summary schema final (verdict + confidence + reason + content_type_tag + style_tag + purpose + read_time + key_points); next is UX brief._
