# Decisions — AIFeeder

Architecturally-shaping calls and the reasoning behind them. Append-only — older decisions stay visible even when superseded.

**Superseding a prior decision:** append a new entry with `**Supersedes:** YYYY-MM-DD — [name]`, and update the old entry's status to `Superseded by YYYY-MM-DD — [name]`. Don't rewrite the old reasoning — the trail of *why* we changed our mind matters as much as the new answer.

**Cross-reference convention** (also in [`CLAUDE.md`](../CLAUDE.md#decisions-log)): every entry should link, where relevant, to:
- [`docs/ideas.md`](ideas.md) — deferred alternatives this decision pushed off
- [`docs/conversation/`](conversation/) — the session where the decision was discussed
- [`docs/state.md`](state.md) — if currently reflected there

Entries are chronological by *when the decision was made*. Entries dated 2026-05-19 or earlier were backfilled on 2026-05-20 from [`handoff.md`](handoff.md).

---

## ~2026-05-19 — In-app reader is non-negotiable

**Status:** Accepted

**Decision:** Items must be readable inside AIFeeder. No "click out to source" as the default consumption path.

**Why:** Clicking out to YouTube / a blog drops the user back into the algorithmic feed we're trying to escape. The mission dies in the click-out. The reader is the mission-defending boundary.

**Tradeoff:** Significantly higher build cost (article extraction + YouTube playback). Some content (paywalled, JS-heavy SPAs) will fall back to "open original" — accepted edge case.

**Refs:** state.md → *Recent decisions › MVP scope*; conversation → [2026-05-19 ideation](conversation/2026-05-19_ideation_mindful-feed.md) (*in-app reader + YouTube playback mode*).

---

## ~2026-05-19 — Per-source "why" + reasoned thumbs feedback (the wedge)

**Status:** Accepted

**Decision:** Every source carries a user-written "why" statement. Thumbs feedback has an optional *reason* field. The reason — not the click — is the personalization signal.

**Why:** Existing readers (Readwise, Feedly + Leo, Recall) all do summaries. None do intent-based, explainable filtering with reasoned feedback. This is the defensible position: (a) intent-based filtering instead of behavioural, (b) explainable spam routing, (c) reasoned feedback rather than clicks.

**Tradeoff:** Higher friction per source and per item — users must articulate intent and rationale. Bet: the target audience finds this rewarding rather than burdensome.

**Refs:** state.md → *Recent decisions › MVP scope*; conversation → [2026-05-19 ideation](conversation/2026-05-19_ideation_mindful-feed.md) (*Narrowing: "why" filter + thumbs feedback with reasons*).

---

## ~2026-05-19 — Subscription business model from day one

**Status:** Accepted — **dormant for v1** (see *2026-05-20 — Local-only, single-user app for v1* below). Reactivates if/when we go public.

**Decision:** Paid subscription ($10–25/mo range). No free tier at scale.

**Why:** Inference economics: ~$300–500K/yr at 1K users following ~20 sources averaging ~3 items/week. Free tier isn't viable. Subscription also aligns incentives — we're not optimizing for ad impressions, which means we're not pressured to engineer engagement-bait.

**Tradeoff:** Acquisition is harder; the addressable market shrinks to people who already value mindful consumption enough to pay. Bet: that's the *only* market that matters for this product.

**Refs:** ideas.md → [Public distribution (auth, multi-tenancy, billing, hosting)](ideas.md) (where this reactivates); conversation → [2026-05-19 ideation](conversation/2026-05-19_ideation_mindful-feed.md) (*Final review: philosophical blindspots + cost reality*).

---

## 2026-05-20 — MVP ingestion: RSS-only

**Status:** Accepted

**Decision:** Only ingest sources that expose RSS. No newsletter email forwarding, no page-diff for non-RSS blogs, no headless-browser fallback, no Twitter / non-RSS social. Sources without RSS are scoped out of v1 entirely.

**Why:** Most high-signal sources do expose RSS (YouTube channel feeds, Substack, most blogs at `/feed`, `/rss`). Covering the long tail is high-cost-per-source. Keep the architecture minimal until we know whether the curation loop is the right wedge.

**Tradeoff:** Twitter (and other RSS-less sources) is real signal we're leaving on the floor. Newsletters likewise. We accept this for scope.

**Refs:** ideas.md → [Twitter / non-RSS source support](ideas.md#twitter--non-rss-source-support), [Newsletter email forwarding](ideas.md#newsletter-email-forwarding), [Page-diff ingestion](ideas.md#page-diff-ingestion-changedetectionio-reference), [Agent-driven headless-browser discovery](ideas.md#agent-driven-headless-browser-discovery); state.md → *Recent decisions › MVP scope*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md) (technical-decisions narrowing turn).

---

## 2026-05-20 — YouTube playback: iframe embed (not custom audio+transcript mode)

**Status:** Accepted, **tracked tradeoff**

**Decision:** Use the standard YouTube iframe embed inside the in-app reader. Do not build the custom audio + transcript + thumbnail player in MVP.

**Why:** The custom player is significantly more complex (custom audio, transcript-sync UI, fallback handling) and YouTube ToS gray area for monetized audio extraction. Iframe is one HTML element. The mission cost (recommendation-surface leak via end-cards) is real but accepted for v1.

**Tradeoff:** iframe end-cards reintroduce the YouTube recommendation surface — the exact thing the custom player was designed to block. Mitigations available (`rel=0`, `modestbranding=1`) but end-cards are creator-controlled. **Track real-user impact in MVP** — if users tell us they get pulled into YouTube via end-cards, the custom player moves back on the table.

**Refs:** ideas.md → [Audio + transcript + thumbnail YouTube mode](ideas.md#audio--transcript--thumbnail-youtube-mode); state.md → *Recent decisions › MVP scope*, *Open questions › iframe vs. recommendation-surface leak*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md) (iframe Q&A).

---

## 2026-05-20 — YouTube transcripts: `yt-dlp` only, no Whisper

**Status:** Accepted

**Decision:** Use `yt-dlp` to fetch auto-generated captions. Videos without captions are skipped in MVP.

**Why:** Whisper inference adds non-trivial per-video cost; ~90–95% of YouTube content has auto-captions; the missing ~5–10% isn't worth the cost+complexity overhead in MVP.

**Tradeoff:** Older / non-English / niche content disproportionately lacks captions and gets dropped. Acceptable for v1.

**Refs:** ideas.md → [Whisper fallback for YouTube transcripts](ideas.md#whisper-fallback-for-youtube-transcripts); state.md → *Recent decisions › MVP scope*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md).

---

## 2026-05-20 — "Library" in MVP is a simple read-archive, not the v2 cluster

**Status:** Accepted

**Decision:** When the user gives feedback or clicks "read", the item disappears from the feed and is archived to their "library" — a simple list of consumed items. This is distinct from the elaborate library/journal/quests cluster envisioned in handoff §4, which stays deferred.

**Why:** Two different needs got the same name. The MVP one (where do read items go?) is a UX necessity for a clean feed. The v2 one (notes / cross-links / journal / quests) is its own design problem that deserves its own design pass — not a bolt-on.

**Tradeoff:** Some users will expect the richer surface and find the MVP version thin. That's fine — naming is "library", not "personal knowledge base".

**Refs:** ideas.md → [The "v2 cluster"](ideas.md#the-v2-cluster--richer-library-journal-intellectual-challenge-quests); state.md → *Recent decisions › MVP scope*, *Features deferred*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md) (library dual-meaning split).

---

## 2026-05-20 — Content-type classification at ingestion, surfaced as a tag

**Status:** Accepted

**Decision:** Every ingested item gets classified by content type (e.g. "tutorial", "news", "philosophical debate", "vlog"). The type is shown as a tag in the list view and feeds the summary-prompting pipeline.

**Why:** Two purposes. (1) UX — users want to know *what kind of thing* this is before clicking. (2) AI pipeline — different content types compress differently; the summary prompt should adapt (see open question 1).

**Tradeoff:** Classification can be wrong; mis-tagging risks user trust. Need a confidence threshold and probably a user-override.

**Refs:** state.md → *Recent decisions › MVP scope*, *Open questions › content-type prompt design*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md).

---

## 2026-05-20 — Two summary outputs: key points + content index, "glimpse not substitute"

**Status:** Accepted

**Decision:** Per-item AI produces (a) a key-points summary, and (b) a content index / chapter structure. Both are framed as a *glimpse* into the content to help the viewer decide whether to engage — not as a substitute for the content itself.

**Why:** The author's presentation matters and doesn't compress. Substitute-summaries also erode creator economics. The glimpse framing both serves the viewer and is gentler on creators.

**Tradeoff:** Two outputs per item ~doubles AI cost per item vs. a single summary. Worth it: the chapter index is what makes a 45-minute video actionable.

**Open follow-on:** content-type-adaptive prompt design (open question 1). E.g. for a debate, key points are framed as "idea X vs. idea Y", not separate pro/con bullets. Needs a research pass to define major content-format categories and per-type prompt shapes.

**Refs:** state.md → *Recent decisions › MVP scope*, *Open questions › content-type prompt design*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md).

---

## 2026-05-20 — Periodic "why" revisits in MVP, triggered by feedback-pattern shifts

**Status:** Accepted

**Decision:** The AI watches for shifts in the user's feedback patterns (e.g. consistently downvoting items that previously matched the "why"). When detected, prompt the user to revisit / update the source's "why".

**Why:** The strict intent filter is a comfort-zone reinforcement machine over time (handoff §7). The revisit prompt is the antibody. The feedback-loop trigger is available now; the insights-driven trigger (deferred) is a richer signal we'll add later.

**Tradeoff:** Bad prompt cadence becomes nagging. Need careful frequency capping. Also: users may *want* their "why" stable — drift isn't always a problem.

**Refs:** ideas.md → [Periodic "why" revisits — insight-shift trigger](ideas.md#periodic-why-revisits--insight-shift-trigger); state.md → *Recent decisions › MVP scope*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md).

---

## 2026-05-20 — No notifications, no unread counts, no streaks

**Status:** Accepted

**Decision:** No push notifications. No unread-count badges. No streak counters. No engagement-style numerics anywhere in the UI.

**Why:** Every one of those is engineered to compel returning to the app. The mission is *not* to compel returning. If a feature feels at home in TikTok, it doesn't belong here.

**Tradeoff:** Retention metrics (DAU, session length) will look bad by mainstream standards. That's the point — we measure mission-aligned metrics (sources curated, items filtered with correct reason, user-reported value), not engagement. Investors / collaborators who expect engagement-style dashboards need to be set straight up front.

**Refs:** state.md → *Recent decisions › MVP scope*, *Gotchas › Never instrument engagement metrics*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md).

---

## 2026-05-20 — Local-only, single-user app for v1

**Status:** Accepted; the "no forward-compat scaffolding" line was **partially superseded** by *2026-05-21 — `users` table in v1 schema* (the `users` parent table is now in v1; `items.user_id` etc. are still deferred).

**Decision:** AIFeeder v1 runs locally on the builder's own machine, single-user only. No auth, no hosting, no multi-tenancy, no subscription billing. **Schema is designed purely for a single user — no `user_id` forward-compat scaffolding.** If we later decide to distribute publicly, schema migration is accepted as the cost.

**Why:** Drops roughly 40–50% of the build (auth, billing, hosting, multi-user cache-sharing, multi-tenant cost telemetry attribution). Lets us validate the curation loop end-to-end before paying the multi-tenant complexity tax. The mission is mindful consumption — proving it works for one user (the builder) is enough to know whether the wedge holds.

**Tradeoff:** Distribution is deferred, *not solved*. If we later go public, we'll need to retrofit: auth, schema migration for multi-tenancy, billing, hosting, ToS / privacy policy — roughly 15–25 hours of engineering plus operational setup. We explicitly accept this cost rather than pay forward-compat complexity now for a future that may not happen.

**Refs:** ideas.md → [Public distribution (auth, multi-tenancy, billing, hosting)](ideas.md); state.md → *Recent decisions › MVP scope*; conversation → [2026-05-20 session](conversation/2026-05-20_b670.md) (local-only scope-cut turn).

---

## 2026-05-20 — Single general AI summary prompt; defer content-type-adaptive prompting

**Status:** Accepted

**Decision:** v1 uses a single general AI prompt for summarization, regardless of content type. The prompt instructs the model to use its own discretion about what shape of summary best fits the content it receives. Per-content-type prompt design (debate-shaped, tutorial-shaped, essay-shaped, etc.) is deferred.

**Why:** The adaptive-prompting research was the biggest remaining rock in MVP (~4–8 hours of iterative prompt design, the riskiest item). Modern LLMs handle per-content-type adaptation reasonably well with a well-written single prompt — losing some fidelity vs. dedicated prompts, but gaining a shippable v1. Defer the fidelity push until we see *which* content types actually produce visibly poor summaries.

**Tradeoff:** Lower summary quality for content that resists generic summarization — long philosophical essays, multi-position debates, narrative pieces. Accepted; we watch which types fail in practice and prioritize those when adaptive prompting comes back.

**Important caveat — content-type tag stays.** Content-type classification still happens (as a parallel output of the summarization call, or a tiny separate classification sub-call) and surfaces as a tag in the list view. The classification is **display-only** in v1 — it does NOT route the summary prompt.

**Refs:** ideas.md → [Content-type-adaptive prompt design](ideas.md); state.md → *Recent decisions › MVP scope* (single general prompt + classification tag display); conversation → [2026-05-20 session](conversation/2026-05-20_b670.md) (adaptive-prompting defer turn).

---

## 2026-05-21 — Add `purpose` + `read_time_estimate` to AI summary schema

**Status:** Accepted

**Decision:** The AI summary now produces two additional fields alongside the existing `relevance_verdict` / `confidence` / `relevance_reason` / `content_type_tag` / `key_points`:
- **`purpose`** — one short sentence describing what the *author* is trying to do (in author-voice). Orthogonal to `relevance_reason` (which is *why the user should care*).
- **`read_time_estimate`** — enum `quick` (<5 min) / `medium` (5–15 min) / `long` (>15 min). Inferred from cues when only an excerpt is provided.

**Why:** First A-checkpoint of real outputs showed `verdict + confidence + reason + key_points` was almost enough but two decision-relevant questions weren't answered: *what is this piece doing* (author intent, separate from user-fit) and *how much of my time does it cost*. The second is critical for the mindful-consumption mission — verdict tells you *if*, time bucket tells you *if-now*.

**Tradeoff:** Two extra fields = slightly more output tokens, slightly more screen real estate in the list view, slight added risk that `purpose` and `relevance_reason` drift toward redundancy. Rejected `target_audience` for exactly that redundancy reason (overlaps heavily with `relevance_reason`).

**Schema:** `summaries` table gets `purpose TEXT` + `read_time_estimate TEXT CHECK (… IN ('quick','medium','long'))`. Both nullable for forward-flex; function-call schema marks both required so the model fills them.

**Refs:** decisions.md → *2026-05-20 — Single general AI summary prompt* (this is the same prompt — fields added, not separated by content type); conversation → [2026-05-20_b670.md](conversation/2026-05-20_b670.md); state.md → *Recent decisions › AI prompt design (locked)* will need an update.

---

## 2026-05-21 — Add orthogonal `style_tag` alongside `content_type_tag`

**Status:** Accepted

**Decision:** Add a second tag field, `style_tag`, with a fixed 7-value vocabulary: `technical-deep-dive`, `explainer`, `opinionated`, `conversational`, `reflective`, `news-brief`, `narrative`. The existing `content_type_tag` continues to capture *format* (essay / tutorial / news / etc.); `style_tag` captures *style*. Both required, both single-valued — total of two tags surfaced per item.

**Why:** During the A-checkpoint the user wanted "up to 2 categories" hinting at "format and the style." Considered three shapes: (1) extend `content_type_tag` to an array of 1–2, (2) add an orthogonal `style_tag`, (3) collapse to one mixed `tags[]` array. Chose (2) because format and style are genuinely orthogonal (an essay can be technical-deep-dive *or* opinionated *or* reflective) and an explicit two-field shape keeps the taxonomy clean — option (1) would produce ambiguous arrays like `[essay, opinionated]` mixing the two axes; option (3) collapses signal that's actually distinct.

**Tradeoff:** Two enums to maintain instead of one. Slight risk of the model picking a style that doesn't fit the format (e.g. `news-brief` style on a tutorial format) — accepted; we'll watch for it in practice. Total summary now has *three* classification fields (content_type_tag, style_tag, read_time_estimate) plus verdict / confidence / reason / purpose / key_points — at the edge of "too many fields" for the list view. UX brief is the moment to decide what surfaces in the list vs. the detail view.

**Refs:** decisions.md → *2026-05-21 — Add `purpose` + `read_time_estimate`* (same A-checkpoint, same prompt); conversation → [2026-05-20_b670.md](conversation/2026-05-20_b670.md).

---

## 2026-05-21 — `users` table in v1 schema (single-row, forward-compatible)

**Status:** Accepted — **partial supersession** of *2026-05-20 — Local-only, single-user app for v1* on the "no `user_id` forward-compat scaffolding" line.

**Decision:** Add a `users` table to the schema even though v1 is single-user. Shape: `users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`. Single row seeded at `init` time. Templates read `{{ user.name }}` instead of a hardcoded string or env-var lookup.

**Why:** This started as a B-question — "where does the username come from for the home-page header `[username]'s Feed`?" — with three options (hardcoded, env var, `users` table). User pushed back: "don't hardcode. add users table." Escalated B→A because (a) it touches schema shape, (b) it pre-resolves part of the future public-distribution retrofit cost (the `users` row already exists; future multi-tenancy adds `user_id` foreign keys on `items` / `feedback` but doesn't need to create the parent table from scratch), (c) the original 2026-05-20 local-only decision explicitly said *no forward-compat scaffolding* — this is a small, considered relaxation of that.

**Tradeoff:** Mild contradiction with the original 2026-05-20 "no forward-compat scaffolding" line — we're paying ~30 lines of schema + init code for a row that v1 never queries with `WHERE user_id = ?`. Accepted as a tiny scope cost for cleaner template ergonomics + a smaller future migration. Does *not* extend to `items.user_id` etc. — those still get added during the public-distribution migration if that ever happens.

**Refs:** decisions.md → *2026-05-20 — Local-only, single-user app for v1* (partial supersession on the scaffolding line); ideas.md → [Public distribution (auth, multi-tenancy, billing, hosting)](ideas.md#public-distribution-auth-multi-tenancy-billing-hosting); engineering-decisions.md → *2026-05-21 — /plan-feature open-Q resolutions (cluster) › b. users table*; conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 17:05 entry).

---

## 2026-05-21 — Home cards stay unchanged after feedback (no hide, no reflow, no dim)

**Status:** Accepted — **provisional** (user flagged the home-page intentionality as still-evolving; "stay unchanged" is the v1 default, not a forever rule)

**Decision:** When the user submits feedback (thumbs up or down) or returns from a content page, the card on home stays exactly as it was — same position, same opacity, same visual weight. No removal, no reflow, no dimming, no "read" indicator.

**Why:** The home page in v1 is "anything the AI recommended" — not "unread items only" and not "items you haven't engaged with." Hiding cards on thumbs-down would push the app toward the inbox-zero pattern (clear the feed = ritual reward), which is the mainstream-reader trap the mission explicitly rejects. Dimming or marking-read would push toward a progress-meter feel. Keeping cards unchanged preserves the journal / library posture — the feed is a *place you visit*, not a queue you clear.

**Tradeoff:** Cards already engaged with will reappear identical across sessions until the AI surfaces something newer; user may scan past them repeatedly. Accepted in v1 because the alternative (any kind of read-state indicator) introduces gamification risk. The dimming-on-scroll-through idea is parked in [ideas.md → UI/UX → Read-state indicator on home cards](ideas.md#uiux-read-state-indicator-on-home-cards-dimming--opacity) as a *future* option to revisit only if the user catches themselves re-scanning past read cards as a real friction, *not* as a default.

**Open follow-on:** What does the home page *intentionally show*? "Anything AI-recommended" is the v1 answer, but the user explicitly flagged this as not-fully-resolved. When that question gets a sharper answer, this decision may need a revisit — the right card-state behaviour depends on what the feed is *for*.

**Refs:** ideas.md → [Read-state indicator on home cards (dimming / opacity)](ideas.md#uiux-read-state-indicator-on-home-cards-dimming--opacity); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 17:05 entry).

---

## 2026-05-21 — Sidebar default state: open on home, collapsed on content

**Status:** Accepted

**Decision:** Sidebar is visible-and-expanded by default on the home page. On the content page, the sidebar starts collapsed (chevron visible to expand). Loading page has no sidebar at all (per the 2026-05-20 design lock).

**Why:** The two pages have different jobs. Home is browsing/scanning — the persona avatar + source list + nav are part of the orientation surface, so sidebar belongs visible. Content is reading — single-column 680px serif column wants minimal chrome, the reader gets the full focal width. Different defaults match different intentionalities.

**Tradeoff:** Two different defaults means the user has to learn the pattern (vs. one consistent default). Accepted because the asymmetry tracks the actual UX of the two pages — and the chevron is always available either way, so the user can override per-page if a preference emerges. If a single consistent default starts feeling cleaner, "always open" is the safer fallback (open-by-default keeps the avatar reminder + nav present always) — re-evaluate after a few real reading sessions.

**Refs:** state.md → *Recent decisions › Pages + nav*; engineering-decisions.md → *2026-05-21 — /plan-feature open-Q resolutions (cluster)*; conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 17:05 entry).

---

## 2026-05-21 — Cards are colour-only in v1; no thumbnail / snapshot images

**Status:** Accepted — **provisional** (user explicitly flagged thumbnails as a future want)

**Decision:** v1 home-page cards display title + "why" + read-time pill + small category + accent-stripe-coloured-by-content-type. **No image element.** Sources without reliable hero images (ArXiv has none, RSS variable) get colour-only cards uniformly — no per-source asymmetry.

**Why:** Two reasons. (1) **No reliable ingestion path** — RSS sometimes has `<media:thumbnail>`, ArXiv doesn't, Simon's blog is mixed. Building per-source extractors is ingestion work that doesn't belong in the UI build. (2) **Mission tension** — image-heavy cards push toward visual-feed scanning (Instagram/Pinterest pattern), where colour-only + serif title + sentence-based "why" pushes toward word-led / reading-led scanning (journal/library pattern). Aligned with the mindful posture.

**Tradeoff:** Slower visual recognition for power-users who'd benefit from a glance-level cue. Accepted in v1 because the alternative requires either (a) ingestion-side image extraction (complex, per-source) or (b) auto-generated AI visuals (terrible idea — drift toward decorative noise). The thumbnail idea is parked in [ideas.md → UI/UX → Card snapshot / thumbnail image](ideas.md#uiux-card-snapshot--thumbnail-image) with the user's explicit "future i want a snapshot to get a glimpse / thumbnail of the content" — to revisit when (a) the user notices themselves scanning cards slowly, or (b) we add a source that reliably ships hero images.

**Refs:** ideas.md → [Card snapshot / thumbnail image](ideas.md#uiux-card-snapshot--thumbnail-image); engineering-decisions.md → *2026-05-21 — /plan-feature open-Q resolutions (cluster)*; conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 17:05 entry).

---

_Last updated: 2026-05-21 — added 4 A-decisions from the /plan-feature open-Q resolution turn (users table B→A escalation, no-card-change on feedback, sidebar defaults, no-thumbnails-v1). Establishes the [completeness rule](../CLAUDE.md#completeness-rule--no-concrete-decision-lives-only-in-conversation) cadence: every answered open Q now lands here or in engineering-decisions.md, not just in the conversation log._
