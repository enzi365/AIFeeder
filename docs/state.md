# Project state — AIFeeder (Mindful Content Feed)

## Current focus

**UX design phase complete — 18 decisions locked; about to enter the build.** AI prompt + summarization pipeline shipped + validated; design conversation captured in [`docs/conversation/2026-05-20_b670_ux-design.md`](conversation/2026-05-20_b670_ux-design.md). Next is `/plan-feature` to scope the FastAPI + HTMX + Jinja2 build (templates, routes, static, css system, faked notes/favs), then build, then wire `refresh`, then real-world test.

Working title: *Mindful Content Feed* — intent-filtered, mindful consumption. v1 audience: the builder.

## Recent decisions

Full A-category reasoning in [`docs/decisions.md`](decisions.md); B-category engineering choices in [`docs/engineering-decisions.md`](engineering-decisions.md). UX/UI deliberation in [`docs/conversation/2026-05-20_b670_ux-design.md`](conversation/2026-05-20_b670_ux-design.md). Most relevant since last refresh:

- **Stylistic system locked.** Fraunces display + Source Serif Pro / Lora body; sepia bg `#F5EBDD`-ish; ink `#3D2C1E` umber not pure black; paper-noise <3%; card body slightly lighter cream than page bg.
- **Welcome tag:** "What's worth your time today?" (invitational, not instructional).
- **Pages + nav:** loading → home → content. Sidebar visible on home + content, **not loading**, collapsible via chevron. Sidebar contents: + / gear / avatar (top row), library, favourites, **notes** (new), alphabetical source list (logo left, name right), persona avatar at bottom (hover → translucent thought-bubbles).
- **Loading page:** centred welcome tag + animated colourful circles. Circles carry per-source whys; **circles overlap with `mix-blend-mode` colour-blending** for watercolour palette mix; 2 text-bearing circles + 4–6 decorative empty ones to avoid sparseness with only 2 sources. Click anywhere → radial fly-out → home.
- **Persona avatar:** flat SVG silhouette + warm radial gradient + drop-shadow + slow pulse-glow (literal 3D deferred to [ideas.md → UI/UX](ideas.md)). Sidebar-only — removed from loading page (focal hierarchy cleaner).
- **Home page cards:** masonry layout (video 2×1, text/PDF 1×2, 3-col grid). Always-visible: title · "why" · read-time · category (small) · snapshot. Hover-reveal: purpose · key points (within-card overlay, no grid reflow). Style + confidence dropped from list. Single accent stripe / title underline coloured by 3 palette families mapped from 9 content types.
- **Content page:** sticky-note "why" callout above body; ~680px serif reader column for `raw_content`. Bottom-right buttons in 3 visual slots: (↑ ↓ paired tight) · pen · star. Up/down arrows as icons (not thumbs). **Tap-to-commit** — friction lives in the follow-up callout ("which why did it fit?" / "what about this didn't fit?"), not the gesture.
- **Notes + favourites:** UI-faked v1 with placeholder data. Real schema (notes table + favourites store, or extend `feedback`) lands with `refresh`.
- **New ship-checkpoint skill** at [`.claude/commands/ship-checkpoint.md`](../.claude/commands/ship-checkpoint.md) — wraps state refresh + stage + commit-draft + /compact hint into one command.

### 5-hour slice scope (unchanged)

- **Sources:** Simon Willison (RSS) + ArXiv `cs.AI` (RSS). **Struthless YouTube still deferred** to next session (yt-dlp ~2 hrs).
- **In:** RSS ingest, AI summarize, list view, detail view, manual refresh, "open original" link.
- **Out (schema ready, UI deferred):** thumbs feedback persistence, library archive UI, source mgmt UI, sortable list, cost dashboard, chapter index, periodic "why" revisit. (UI shells for notes + favourites exist in v1 but data is faked.)

### Failure recovery (locked, not yet wired)

Transient → 3 retries with exponential backoff (1s/4s/16s); permanent → no retry; content-level → skip; unknown → 1 retry then permanent. Sources with `consecutive_failures >= 3` get a `!` icon. Schema columns exist; logic lands with `refresh`.

## Open questions

1. **Source of "user-level whys" (deferred).** v1 loading page uses per-source whys directly. A future surface might want AI-derived user-level intent statements from per-source whys + feedback — flagged but not blocking; revisit when persona pipeline gets real attention.
2. **Ritual fit.** Replace doomscrolling without becoming another "must check" app. Still load-bearing through build.
3. **iframe vs. recommendation-surface leak.** Not relevant in v1 slice (no YouTube). Tracked for v2.

## Next steps

In order:

1. **`/plan-feature`** to scope the FastAPI + HTMX + Jinja2 build (templates, routes, static, css system, faked notes/favs interactions). Plan-then-build, not type-and-hope.
2. **Build UI** — 4 pages per locked design. ~1 hour target.
3. **Wire `refresh` subcommand** — ingest + summarize + persist to DB (currently raises `NotImplementedError`). Includes failure-recovery retry policy.
4. **Add failure-class detection** to ingest + ai paths; populate `consecutive_failures` / `last_error_*` on sources.
5. **Real-world test** + fix top 1–2 issues.
6. **Next session:** YouTube/Struthless (`yt-dlp` + transcript pipeline); real notes/favourites schema.

## Gotchas / quirks

- **UX design conversation lives in [`docs/conversation/2026-05-20_b670_ux-design.md`](conversation/2026-05-20_b670_ux-design.md)** — topic-split from the main b670 file. Main file kept AI-prompt + scaffolding work. When loading session context, read both.
- **Notes + favourites are UI-faked in v1** — clicking the pen/star buttons works visually but doesn't persist. Schema additions land with `refresh` wiring.
- **Three parallel Claude Code sessions ran on this checkout earlier** (b670 = strategy + scaffold + AI + UX; 10ca = hook debugging; 4dac = git/auth setup). `state.md` is single-writer — serialise `/state` between concurrent sessions or use `git worktree` for branch-divergent work.
- **Schema includes future-MVP columns the slice doesn't use yet** (`failure_class`, `failure_message`, `consecutive_failures`, `last_error_at`, `last_error_message`, `is_read`, `feedback` table, `chapter_index_json`).
- **`preview` auto-applies the schema** — was opaque sqlite errors before; now idempotent.
- **DB file is local-only.** If you ran `aifeeder init` before the latest schema additions (`purpose`, `style_tag`, `read_time_estimate`), `refresh` will fail on write. Solution: delete the file and re-`init`. No data lost — nothing persisted yet.
- **"Open original" link bypasses in-app reader in v1 slice.** Fine for Simon + ArXiv. Mission-compromise flag lights up when YouTube enters v2.
- **`docs/handoff.md` and `docs/my-log.md` intentionally untracked** — never `git add .` or `-A`; always stage explicitly. The `/ship-checkpoint` skill stages explicitly by path.
- **Never instrument engagement metrics** (DAU, session length). Mission-aligned metrics only.
- **The mindfulness paradox** — every UX decision: if it would feel at home in TikTok, it doesn't belong here.
- **AI prompt tone is A-category.** If quality is off after more outputs, iterate the prompt — never the tone phrasings ("Worth reading if…" / "Worth a shot for X although Y" / "Skip — this is mostly Z") without user sign-off.
- **Conversation log format:** per-turn entries are brief **Me:** / **Claude:** intent-summary — never a verbatim repaste of the chat reply, even when in-character (designer mode, etc.). Memory rule: [feedback_conversation-log-no-transcripting](/home/emma/.claude/projects/-home-emma-Workspace-Make-Land-AIFeeder/memory/feedback_conversation-log-no-transcripting.md).
- **IDE flags `schema.sql` errors** — false positives from the MSSQL language server; file is valid SQLite.

_Last updated: 2026-05-21 — UX design phase complete (18 decisions locked); next is `/plan-feature` then the FastAPI + HTMX + Jinja2 build._
