# Project state — AIFeeder (Mindful Content Feed)

## Current focus

Strategic questions resolved on 2026-05-20. Scope cut further: **v1 is a local-only, single-user app** (no auth, no multi-tenancy, no hosting, no billing). Next: pick the tech stack + sketch schema + write first cut of the AI prompt, then build.

Working title: *Mindful Content Feed* — intent-filtered, mindful consumption. v1 audience: the builder.

## Recent decisions

Full reasoning in [`docs/decisions.md`](decisions.md). Summary:

### MVP scope (locked 2026-05-20)

- **Local-only, single-user.** Runs on the builder's own machine. No auth, no hosting, no billing, no multi-tenancy. Schema is single-user-only — no `user_id` forward-compat. Distribution is deferred to [ideas.md](ideas.md), explicitly accepting future migration cost.
- **Source management** with per-source "why".
- **Periodic ingestion via RSS only.** No Twitter/non-RSS, no page-diff, no headless browser, no email forwarding.
- **Per-item AI processing — three outputs from a single general prompt:**
  1. **Relevance verdict** against the source's "why" (with reason).
  2. **Key points summary** — "glimpse, not substitute".
  3. **Content index / chapter structure** — the YouTube-chapter equivalent.
  - **Single general prompt** — no content-type-adaptive prompting in v1. The model uses its discretion. Adaptive prompting deferred to [ideas.md](ideas.md).
- **Content-type classification at ingestion**, surfaced as a **tag in the list view** (e.g. "tutorial", "news", "debate", "vlog"). **Display-only** in v1 — does not route the summary prompt.
- **In-app reader.**
  - Articles: Mozilla Readability / `@postlight/parser` (~85% extraction quality accepted).
  - YouTube: **iframe embed** (no custom audio+transcript+thumbnail mode). Tradeoff: iframe end-cards reintroduce YouTube's recommendation surface — track real-user impact.
- **YouTube transcripts:** `yt-dlp` only. No Whisper fallback — captionless videos are skipped.
- **Thumbs feedback with optional *reason* field.** The reason is the personalization signal.
- **Periodic "why" revisit prompts**, triggered by feedback-pattern shifts.
- **List view + clean feed.** Sortable by date or relevance score. **No push notifications, no unread counts, no streaks.** When the user gives feedback or clicks "read", the item disappears and is archived to their **library** (simple read-archive — *not* the elaborate library/journal/quests cluster).
- **Cost telemetry (lightweight)** — per-item cost stored in DB so the builder can see monthly spend. No dashboards.

### Business model

Subscription model is **dormant** for v1 (local-only, no users to bill). The "$10–25/mo from day one" decision reactivates if/when distribution happens — see [ideas.md → Public distribution](ideas.md).

### Features deferred

[`docs/ideas.md`](ideas.md). New additions this turn: **content-type-adaptive prompt design**, **public distribution (auth, multi-tenancy, billing, hosting)**.

## Open questions

1. **Tech stack** — frontend (browser-rendered? Electron? CLI + local web UI?), backend framework, DB (SQLite is the obvious pick), LLM provider (Claude API? local model via Ollama? both behind a thin abstraction?). Settle before scaffolding.
2. **Ritual fit, refined.** User-stated conflict from 2026-05-20: replace doomscrolling without becoming another "must check" app. Candidate patterns: (a) trigger-replacement (home-screen / new-tab placement), (b) "empty feed" UX ("you're up to date — see you tomorrow"), (c) celebrate filtering wins, not consumption volume. Resolve before reader UI.
3. **iframe vs. recommendation-surface leak** — accepted iframe for v1 scope, but it reintroduces YouTube end-cards. Track impact; revisit custom player if real use shows pulls into YouTube.

## Next steps

1. ~~Decide the five strategic questions.~~ ✅ (2026-05-20)
2. ~~Cut scope to local-only, single-user.~~ ✅ (2026-05-20)
3. **Pick tech stack + sketch schema + write first cut of the general AI prompt.** This is the next session — likely a `/plan-feature` for the vertical slice.
4. Build RSS ingestion → DB → AI pipeline → list view → reader, in that order.

## Gotchas / quirks

- **iframe end-cards leak YouTube's recommendation surface.** Accepted MVP tradeoff — track impact.
- **YouTube ToS is more relaxed for personal use.** `yt-dlp` and iframe both fine for v1; tightens significantly if/when we distribute.
- **No cross-user cache.** Local-only collapses the "1 summary for N users" gotcha; per-item caching is still useful (don't re-summarize the same article twice) but much simpler design.
- **Lightweight cost telemetry.** Store per-item cost in the DB; query when curious. Skip dashboards.
- **Never instrument engagement metrics** (DAU, session length). Track mission-aligned metrics only.
- **AI provider abstraction is optional in v1** but cheap — a thin interface lets you swap Claude ↔ local model without rewriting the pipeline.
- **Privacy story is trivial for v1** — data stays on the user's machine except when sent to the LLM provider, which is a knob they control.
- **The mindfulness paradox** — every UX decision: if it feels at home in TikTok, it doesn't belong here.
- **Single-user schema commits to a migration cost later.** If distribution happens, schema + data migration is non-trivial. Accepted.

_Last updated: 2026-05-20 — local-only single-user scope cut; single general AI prompt (adaptive deferred); content-type tag retained as display-only; cost telemetry kept (lightweight); subscription model marked dormant._
