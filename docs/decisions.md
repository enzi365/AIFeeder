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

## 2026-05-21 — Feedback affordance: thumbs up/down (supersedes "icon arrows not thumbs")

**Status:** Accepted — **Supersedes:** 2026-05-20 UX-lock line "up/down arrows as icons NOT thumbs"

**Decision:** The content-page feedback buttons use thumbs-up / thumbs-down icons. Replaces the up-arrow / down-arrow icons that were locked during the 2026-05-20 UX design pass.

**Why:** First browser-check of the rendered UI; the user explicitly asked for thumbs. The original rationale for arrows-not-thumbs was that thumbs felt social-media-coded; in practice the user found the universal feedback mental model (thumbs = approve/disapprove) cleared faster than re-learning that arrows mean the same thing. The arrows-as-icons distinction wasn't carrying the weight the design pass assumed it would.

**Tradeoff:** Thumbs do carry a tiny TikTok/YouTube residue. Mitigated by the *callout* that follows the thumbs (which-why-fit chips / off-topic chips) — the friction lives in the follow-up, not in the gesture, so the mainstream-feeling primitive still hangs off a mindful workflow. Mission heuristic ("if it would feel at home in TikTok, it doesn't belong here") survives because the *interaction model around the thumbs* is what makes this distinct, not the icon shape.

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 browser-check feedback turn); engineering-decisions.md → *2026-05-21 — UI iteration round 1 (cluster)*.

---

## 2026-05-21 — Content-page "why" callout: plain block, not sticky-note

**Status:** Accepted — **Supersedes:** 2026-05-20 UX-lock line "sticky-note 'why' callout above body (slight rotation, soft shadow, warm yellow)"

**Decision:** Replace the rotated yellow sticky-note "why" callout on the content page with a plain rectangular block (same card cream / paper background as the rest of the page). The block carries `purpose` + `key_points` (the same fields surfaced on the home-card hover overlay). Drop the "worth your time" copy and drop `relevance_reason` from this block — relevance_reason already appears on the home card itself.

**Why:** First browser-check; user found the sticky-note styling distracting in the reading context (rotation + shadow + warm-yellow contrast pulled the eye away from the article body). The plain-block treatment keeps the orientation information available without competing with the reader column. Drops `relevance_reason` because by the time the user is on the content page they've already seen + acted on it (clicking through is the implicit "yes, this why fit me").

**Tradeoff:** Loses some of the painterly journal-feel — the sticky-note was one of the elements that distinguished this from a generic reader app. Accepted: the journal-feel survives in the home-card grid, the sidebar persona avatar, the loading-page circles. The reader column was the wrong place to spend whimsy budget; the article body deserves the focal weight.

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 browser-check feedback turn).

---

## 2026-05-21 — Sans-serif body typography (Source Sans 3) alongside Fraunces titles

**Status:** Accepted — **Refines:** the 2026-05-20 typography lock (Fraunces display + Source Serif Pro body)

**Decision:** Body text gets a sans-serif treatment via **Source Sans 3** (Adobe, same designer / metrics as Source Serif Pro). Specifically:
- Sans-serif: card `why` text, content reader body, hover overlay descriptions (under "Purpose" + "Key points" headers), `relevance_reason`-equivalent prose.
- Stays serif (Fraunces or Source Serif Pro): all titles (`h1`–`h4`), tag pills (`read-time`, `content_type_tag`), section headers like "Purpose" / "Key points", sticky monogram letters, sidebar nav labels.

**Why:** First browser-check; user found extended serif body text hard to read in the card context (small font + tight spacing) and the reader context (length × line-height). Source Sans 3 keeps the design cohesion (same family as the existing Source Serif Pro) while improving readability at the small + dense sizes. Titles + headers stay serif because that's where Fraunces does its mindfulness-coded work — sans-serif everything would drift the app toward a generic reader.

**Tradeoff:** One extra Google Fonts request (Source Sans 3 weights). Mild increase in CSS surface area to namespace which elements stay serif vs. go sans. Accepted: cohesion + readability are both load-bearing for the mission.

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 browser-check feedback turn); engineering-decisions.md → *2026-05-21 — UI iteration round 1 (cluster) › Source Sans 3*.

---

## 2026-05-21 — Apple yes/maybe indicators on home cards

**Status:** Accepted

**Decision:** Each home-feed card carries a small inline-SVG apple icon on the bottom-right corner. Two states keyed to `relevance_verdict`:
- **yes** → whole apple (red body with gradient + green leaf)
- **maybe** → 3/4-eaten apple (same red gradient + green leaf, bite shape on the right side)
- **no** → no apple rendered (yes/maybe are the only verdicts surfaced on home anyway per `list_feed_items()` filter)

**Why:** User wants a quick visual signal of how strongly the AI recommends each item, beyond the existing text-only verdict-via-presence ("if it's here, it's yes or maybe"). Apples carry mission-aligned connotations (the orchard / a fruit of consumption, the bitten apple as "engaged-with-but-not-finished" / "this one's worth a partial taste"). Mission-aligned because they signal *health* of the recommendation rather than urgency / unread-counter / progress-bar gamification.

**Tradeoff:** A discrete signifier per card adds tiny visual weight to the masonry grid (mitigated by small size + bottom-right placement, away from title/why focus). Inline SVG carries the same cost as the existing icon macros — no asset pipeline burden. Not a thumbnail (the 2026-05-21 no-thumbnails decision still holds: this is a *discrete* signifier, not a content preview).

**Refs:** decisions.md → *2026-05-21 — Cards are colour-only in v1; no thumbnail / snapshot images* (compatible — apple is a signifier, not a content preview); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 browser-check feedback turn).

---

## 2026-05-21 — In-text highlighting + quote-attached notes (v1 in-memory fake)

**Status:** Accepted — **B→A escalation** (originally a UX feedback item; touches feature scope + persistence model)

**Decision:** On the content page, the user can select text in the reader column, click a floating "+ Note" button that appears near the selection, and the selected text becomes the *quote* attached to a new note. The selection then renders as a persistent highlight (yellow `<mark>`) every time the user re-opens the same article. V1 stores highlights + quoted notes in the existing in-memory fake module (`web/fakes.py`) — wiped on uvicorn reload. Real persistence (SQLite table) lands with the `refresh` wire-up.

**Why:** Reading + note-taking are the same gesture for this user, and the v1 note panel as-designed treated them as two: open the panel, type the title, type the body, no link to *what triggered* the note. The highlight → quote → note chain closes that loop. Persistent highlights matter because the second time the user opens an article they want to see *where they were* — re-reading is a real workflow for the target audience (researchers, deep readers).

**Tradeoff:** Adds JS surface (selection capture + floating button + post-save highlight injection) beyond the ~80 LOC vanilla-JS budget set in the /plan-feature pass. Adds a fake storage shape (`highlights: list[{quote, note_index}]` per item_id) that has to migrate cleanly to a real schema when refresh lands. Re-rendering highlights uses naïve substring matching ("first occurrence of the quoted text in the reader's paragraphs") — fails if the same exact phrase appears twice. Accepted for v1; the corner case can be patched with offset-tracking when real persistence lands.

**Why B→A:** Originally framed as a small UX add. Escalated because (a) it adds a feature *scope* item not in the locked v1 list, (b) it pre-shapes a persistence schema for highlights that the eventual refresh wire-up has to honour, (c) it changes the note-taking *interaction model* from "compose a free-form note" to "quote-anchored notes" as the primary form.

**Refs:** decisions.md → *2026-05-20 — Two summary outputs: key points + content index, "glimpse not substitute"* (highlights are the user's *own* glimpses-into-the-content, parallel to the AI's); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 browser-check feedback turn); engineering-decisions.md → *2026-05-21 — UI iteration round 1 (cluster)*.

---

## 2026-05-21 — Sources are user-editable from the UI (first UI-→-DB write path)

**Status:** Accepted

**Decision:** Clicking a source row in the sidebar opens a centered modal (backdrop blurs the main column but **not** the sidebar) with two fields: the source URL + a single "why" textarea with a persistent helper hint *above* it asking what they value from the source and what they'd rather not receive. Save persists to the real `sources` table (`UPDATE sources SET url = ?, why = ? WHERE id = ?`); Cancel + Esc + click-outside-the-modal all dismiss without saving. This is the **first UI-driven write to a real schema table** in the v1 app (notes / favourites / highlights all use in-memory fakes; sources writes were previously only done by `aifeeder init`).

**Why:** The per-source "why" is one of the two load-bearing wedges of the app (alongside thumbs-with-reasons feedback — see *~2026-05-19 — Per-source "why" + reasoned thumbs feedback*). The user *will* iterate on their whys over time as their consumption pattern matures and as the AI revisit prompts trigger (see *2026-05-20 — Periodic "why" revisits*). Forcing them to drop to a SQL prompt or re-run `init` to edit a why would break the mission rhythm. The URL is similarly mutable — sources move, change subdomains, get archived. Making both editable from the UI is the minimum-viable surface that respects the why's centrality.

**Tradeoff:** Introduces a **UI-→-DB write path** that didn't exist in the v1 plan, which has knock-on effects: (1) a new `web/writes.py` module breaks ground that the read-only `repo.py` deliberately avoided — going forward, other UI features (delete source, archive item, mark-read) have a natural home but also a natural temptation; (2) no undo / version history — accidental edit overwrites the original why with no recovery (acceptable for single-user v1 local, would need rethink for public-distribution); (3) the modal pattern (backdrop + centered card + Esc/click-outside close) becomes the in-house modal convention — future modals should reuse the same shape rather than re-invent.

**Why this is A-category, not B:** Touches **scope** (adds a user-facing write surface not in the v1 plan), **UX** (introduces the modal pattern), and indirectly **mission** (makes the wedge feature ergonomic). The single-textarea-with-hint copy choice + the backdrop-blur-except-sidebar visual treatment are A-shaped too — they shape how the user *feels* about editing their whys, which is load-bearing.

**Open follow-ons:** (a) The orange `+` add-source button in the sidebar should probably eventually use the same modal pattern for *creating* a source (not just editing) — not built today, but the modal partial is structured so it could be reused with empty fields. (b) Delete-source affordance not added — user explicitly didn't ask for it. (c) Modal-pattern lives in [main.css](../src/aifeeder/static/css/main.css) for now; if a third modal lands, factor to its own `modal.css`.

**Refs:** decisions.md → *~2026-05-19 — Per-source "why" + reasoned thumbs feedback (the wedge)* (this decision makes the wedge editable); decisions.md → *2026-05-20 — Local-only, single-user app for v1* (compatible — no auth concerns because single-user, but the UI-write surface adds to the public-distribution retrofit cost flagged there); engineering-decisions.md → *2026-05-21 — Source-edit modal (cluster)*; conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 source-edit modal turn).

---

_Last updated: 2026-05-21 — 6 A-entries from the browser-check + UI-iteration day (thumbs supersedes arrows, plain-block supersedes sticky-note, sans-serif body refines typography lock, apple verdict indicators, in-text highlighting B→A escalation, **sources editable from UI as first UI-→-DB write path**)._

---

## 2026-05-22 — Home card splits the "maybe" verdict into stacked green/orange blocks

**Status:** Accepted

**Decision:** On the home-page card, the AI's `relevance_reason` is rendered as two stacked, **labelless** blocks differentiated only by color and left-border accent. The positive half ("Worth a shot for X" / "Worth reading if X") gets a **soft sage left-border (`--accent-positive-soft #C9D5B0`) + faint sage bg tint**; the caution half ("although Y" / "but Y" / "though Y") gets a **soft sienna left-border (`--accent-warm-soft`) + faint sienna bg tint**. The locked AI tone phrasings are preserved verbatim — the stems ("Worth a shot for…", "although…") are kept, just visually painted. "Yes" verdicts render only the green block; "maybe" verdicts get both stacked. The split happens client-side at render time via `_split_reason()` in [routes.py](../src/aifeeder/web/routes.py), splitting on a case-insensitive regex `\s+(although|but|though)\s+`.

**Why:** User asked for a visual split that separates "what's pulling this in" from "what you should know" — the mindful-feed mission benefits from making the caution as first-class as the recommendation (anti-clickbait: the AI is allowed to hedge visibly). Picked labelless because color + position is enough signal once the convention is visible — a "For you / Heads up" label scheme was offered but rejected as too explicit for what's already a small card. Sage chosen specifically because the existing palette (`warm/cool/neutral` = sienna/teal/umber) had no green; the warm cream card background (`#FAF1E2`) plus a desaturated sage (`#6F8B4F` derived family) feels vintage-aligned rather than tacked-on.

**Tradeoff:** Two costs taken on:
- **Brittle splitter:** Client-side regex on `(although|but|though)` works for 24/24 sampled outputs but assumes the AI keeps using one of those three hinge words. A model swap or prompt tweak that introduces "however" / "though arguably" / "yet" would silently produce a single green block with no caution. Mitigation deferred: revisit by adding an explicit `reason_caution` field to the OpenAI tool-call schema in [ai.py](../src/aifeeder/ai.py), which would make the split structural rather than parsed. Not done now because it's a v1.x cleanup, not a v1 blocker.
- **Locked phrasing dependency on the cards:** The "Worth a shot for…although…" voice now does double duty (console output + visual split anchor). If a future tone refresh changes those stems without also updating the splitter, the cards quietly degrade. Worth checking together.

**Refs:** ideas.md → *(none deferred — alternative options "For you/Heads up labels" and "icon-only" were rejected outright, not parked)*; conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 reason-split turn); engineering-decisions.md → *2026-05-22 — `aifeeder refresh` implementation* (sibling small turn — both shipped same session, refresh first then reason-split as the immediate browser-check tweak).

---

_Last updated: 2026-05-22 — Home card reason-split lands as A-decision (labelless sage/sienna stacked blocks; locked AI voice preserved verbatim; sage added to the palette as `--accent-positive*`)._
